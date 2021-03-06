from django.contrib import admin

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from xshop.core.utils import UserGroup
from xshop.users.models import User
from xshop.shops.models import Shop
from xshop.invoices.models import Invoice
from xshop.products.models import Product
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 2

    def has_add_permission(self, request, obj=None):
        user: User = request.user
        return bool(
            request.user.is_superuser
            or user.type
            and user.type[0] in [UserGroup.CASHIER, UserGroup.GENERAL_MANAGER]
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user: User = request.user
        if not user.is_superuser:
            if db_field.name == "product":
                kwargs["queryset"] = Product.objects.filter(shop=user.shop).order_by(
                    "-id"
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ("id", "user", "shop")
    list_display_links = ("id", "user")
    search_fields = ("user__name", "user__mobile", "shop__name", "shop__mobile")
    ordering = ("-id",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("order",),
                "fields": ("user", "paid"),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    # save methods
    def save_model(self, request, obj, form, change):
        user: User = request.user
        if user.type and user.type[0] in [
            UserGroup.CASHIER.title(),
            UserGroup.GENERAL_MANAGER.title(),
            UserGroup.MANAGER.title(),
        ]:
            obj.shop = user.shop
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        user: User = request.user
        if UserGroup.CASHIER in user.type:
            Invoice.objects.create(user=user, order=obj)
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    # UI methods
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user: User = request.user
        if (
            user.type
            and user.type[0]
            in [
                UserGroup.CASHIER.title(),
                UserGroup.GENERAL_MANAGER.title(),
                UserGroup.MANAGER.title(),
            ]
            and db_field.name == "shop"
        ):
            kwargs["queryset"] = Shop.objects.filter(id=user.shop.id)

        if (
            user.type
            and user.type[0]
            in [
                UserGroup.CASHIER.title(),
                UserGroup.GENERAL_MANAGER.title(),
                UserGroup.MANAGER.title(),
            ]
            and db_field.name == "user"
        ):
            kwargs["disabled"] = True
            kwargs["queryset"] = User.objects.filter(mobile=request.user.mobile)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        user: User = request.user
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        if user.type and user.type[0] in [
            UserGroup.CASHIER.title(),
            UserGroup.GENERAL_MANAGER.title(),
            UserGroup.MANAGER.title(),
        ]:
            self.exclude = ("shop",)
            form.base_fields["user"].initial = user
        return form

    # permissions
    def has_module_permission(self, request):
        user: User = request.user
        try:
            return bool(
                user.is_superuser
                or user.type[0]
                in [
                    UserGroup.CASHIER.title(),
                    UserGroup.GENERAL_MANAGER.title(),
                    UserGroup.MANAGER.title(),
                ]
            )
        except AttributeError:
            return False

    def has_add_permission(self, request, obj=None):
        user: User = request.user
        return bool(
            user.is_superuser
            or user.type[0]
            in [
                UserGroup.CASHIER.title(),
                UserGroup.GENERAL_MANAGER.title(),
                UserGroup.MANAGER.title(),
            ]
        )

    def has_view_permission(self, request, obj=None):
        user: User = request.user
        return bool(
            user.is_superuser
            or user.type[0]
            in [
                UserGroup.CASHIER.title(),
                UserGroup.GENERAL_MANAGER.title(),
                UserGroup.MANAGER.title(),
            ]
        )

    def get_queryset(self, request):
        user: User = request.user
        if user.is_superuser:
            return Order.objects.all()
        if user.type and user.type[0] in [
            UserGroup.CASHIER.title(),
            UserGroup.GENERAL_MANAGER.title(),
            UserGroup.MANAGER.title(),
        ]:
            return Order.objects.filter(shop=user.shop)
        raise PermissionDenied(_("You have no access to this data."))

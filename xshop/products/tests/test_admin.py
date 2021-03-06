from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.core.exceptions import PermissionDenied
from model_bakery import baker
from django.urls import reverse
from django.test import Client

from xshop.users.models import GeneralManager, DataEntryClerk, User
from ...shops.models import Shop
from ..admin import ProductAdmin
from ..models import Product


class MockRequest:
    GET = ""

    def get(self):
        request_factory = RequestFactory()
        return request_factory.get("/admin")


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


request = MockRequest()
request.user = MockSuperUser()


class ProductAdminTests(TestCase):
    def setUp(self) -> None:
        self.site = AdminSite()
        self.model_admin = ProductAdmin(Product, self.site)

        # shops
        self.shop_test = baker.make(Shop, mobile="01010092182")
        self.shop = baker.make(Shop, mobile="01010092183")
        self.shop1 = baker.make(Shop, mobile="01010092184")

        # product
        self.product_test = baker.make(Product, name="superuser_p", shop=self.shop_test)
        self.product = baker.make(Product, name="manager_p", shop=self.shop)

        # users
        self.superuser = baker.make(User, mobile="01010092181", is_superuser=True)

        self.manager = baker.make(GeneralManager, mobile="01010092183", shop=self.shop)
        self.password_gm = "testpass1234"
        self.manager.set_password(self.password_gm)
        self.manager.save()

        self.manager1 = baker.make(
            GeneralManager, mobile="01010092184", shop=self.shop1
        )

        self.data_entry = baker.make(
            DataEntryClerk, mobile="01010092186", shop=self.shop
        )
        self.password = "testpass123"
        self.data_entry.set_password(self.password)
        self.data_entry.save()

        self.test_user = baker.make(User, mobile="01010092185")
        self.password_user = "testpass12345"
        self.test_user.set_password(self.password_gm)
        self.test_user.save()

        # requests
        self.request_super = MockRequest()
        self.request_super.user = self.superuser

        self.request_manager = MockRequest()
        self.request_manager.user = self.manager

        self.request_no_product = MockRequest()
        self.request_no_product.user = self.manager1

        self.request_data_entry = MockRequest()
        self.request_data_entry.user = self.data_entry

        self.request_no_product1 = MockRequest()
        self.request_no_product1.user = self.data_entry

        self.request_test_user = MockRequest()
        self.request_test_user.user = self.test_user

        # url
        self.client = Client()
        self.url = reverse("admin:products_product_add")

        # attr values

    def test_get_add_order_page_not_authenticated(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 302)

    def test_get_add_order_page_DEC(self):
        self.client.login(mobile=self.data_entry.mobile, password=self.password)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_get_add_order_page_gm(self):
        self.client.login(mobile=self.manager.mobile, password=self.password_gm)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_get_add_order_page_user(self):
        self.client.login(mobile=self.test_user.mobile, password=self.password_user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_superuser_product_queryset(self):
        self.assertEqual(
            list(self.model_admin.get_queryset(self.request_super).order_by("-id")),
            list(Product.objects.all().order_by("-id")),
        )

    def test_manager_product_queryset(self):
        self.assertEqual(
            list(self.model_admin.get_queryset(self.request_manager).order_by("-id")),
            list(Product.objects.filter(shop=self.shop).order_by("-id")),
        )

    def test_manager_no_product_queryset(self):
        self.assertEqual(
            list(
                self.model_admin.get_queryset(self.request_no_product).order_by("-id")
            ),
            list(Product.objects.filter(shop=self.shop1).order_by("-id")),
        )

    def test_manager_permission_denied_product_queryset(self):
        with self.assertRaisesMessage(
            PermissionDenied, "You have no access to this data."
        ):
            self.model_admin.get_queryset(self.request_test_user)

    def test_data_entry_product_queryset(self):
        self.assertEqual(
            list(
                self.model_admin.get_queryset(self.request_data_entry).order_by("-id")
            ),
            list(Product.objects.filter(shop=self.shop).order_by("-id")),
        )

    def test_data_entry_no_product_queryset(self):
        self.assertEqual(
            list(
                self.model_admin.get_queryset(self.request_no_product1).order_by("-id")
            ),
            list(Product.objects.filter(shop=self.shop).order_by("-id")),
        )

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django import forms

from xshop.cart.cart import Cart
from xshop.cart.forms import CartPostProductForm
from xshop.products.models import Product
from xshop.cart.api.serializers import ProdcutCartSerializer


class CartView(LoginRequiredMixin, ListView):
    def post(self, request):
        cart = Cart(request)
        form = CartPostProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            action = cd["actions"]
            product = cd["product"]

            if action == "update":
                quantity = int(cd["quantity"])
                cart.update(
                    product=product,
                    quantity=quantity,
                )

                return redirect("cart:cart_ops")
        if request.POST.get("action") == "update":
            product_id = int(request.POST.get("productid"))
            try:
                product = Product.objects.get(id=product_id)
                product_json = ProdcutCartSerializer(product).data
                quantity = int(request.POST.get("quantity"))
                if product.stock < quantity:
                    raise forms.ValidationError(
                        {"quantity": f"Invalid. available stock {product.stock}"}
                    )
                cart.update(
                    product=product_json,
                    quantity=quantity,
                )

                return redirect("cart:cart_ops")

            except Product.DoesNotExist:
                form.errors["product_id"] = "Not found"

        if request.POST.get("actions") == "add":
            product_id = int(request.POST.get("product_id"))
            try:
                product = Product.objects.get(id=product_id)
                product_json = ProdcutCartSerializer(product).data
                cart.add(product=product_json)

                return redirect("cart:cart_ops")
            except Product.DoesNotExist:
                form.errors["product_id"] = "Not found"

        if request.POST.get("action") == "remove":
            product_id = int(request.POST.get("productid"))
            product = Product.objects.get(id=product_id)
            product_json = ProdcutCartSerializer(product).data
            cart.remove(product_json)
            return redirect("cart:cart_ops")

        if request.POST.get("action") == "clear":
            cart.clear()

            return redirect("cart:cart_ops")

        full_price = 0
        for item in cart:
            full_price += item["total_price"]
            item["update_quantity_form"] = CartPostProductForm(
                initial={
                    "quantity": item["quantity"],
                    "actions": "update",
                    "product_id": item["product"]["id"],
                }
            )
        context = {
            "cart": cart,
            "full_price": full_price,
            "user": request.user,
            "errors": form.errors,
        }
        return render(request, "pages/cart.html", context)

    def get(self, request):
        cart = Cart(request)
        full_price = 0
        for item in cart:
            full_price += item["total_price"]
            item["update_quantity_form"] = CartPostProductForm(
                initial={
                    "quantity": item["quantity"],
                    "actions": "update",
                    "product_id": item["product"]["id"],
                }
            )
        context = {
            "cart": cart,
            "full_price": full_price,
            "user": request.user,
            "quantity_range": range(1, 10),
            "ui": range(12),
        }
        return render(request, "pages/cart.html", context)

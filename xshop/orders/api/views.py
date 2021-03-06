import uuid


from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from ..models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
from xshop.products.models import Product
from xshop.payments import paymob
from xshop.payments.models import PaymentAttempt
from xshop.core.utils import UserGroup


class OrderListCreateApi(APIView):
    serializer_class = OrderSerializer

    @extend_schema(
        description="List all orders",
        responses={200: "orders list"},
    )
    def get(self, request):
        user = request.user
        if user.is_superuser:
            orders = Order.objects.all()
        elif user.type and bool(
            user.type[0]
            in [
                UserGroup.GENERAL_MANAGER.title(),
                UserGroup.CASHIER.title(),
            ]
        ):
            orders = Order.objects.filter(shop=user.shop)
        elif user.type and bool(
            user.type[0]
            in [
                UserGroup.DATA_ENTRY_CLERK.title(),
                UserGroup.CUSTOMER.title(),
            ]
        ):
            orders = Order.objects.filter(user=user)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Create new Order",
        request=OrderSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_order = serializer.save()
        return Response(self.serializer_class(new_order).data)


class OrderDetailPatchApi(APIView):
    serializer_class = OrderSerializer

    @extend_schema(
        description="Get Order details",
        responses={200: OrderSerializer, 404: "Order not found"},
    )
    def get(self, request, order_id):
        user = request.user
        order = get_object_or_404(Order, id=order_id)
        if not user.is_superuser and (order.user != user or order.shop != user.shop):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(order, many=False)
        return Response(serializer.data)

    @extend_schema(
        description="Patch existing Order",
        request=OrderSerializer,
        responses={404: "Order does not exist"},
    )
    def patch(self, request, order_id):
        user = request.user
        order = get_object_or_404(Order, id=order_id)
        if order.user != user or order.shop != user.shop or not user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_order = serializer.save()
        return Response(self.serializer_class(updated_order).data)


class CheckoutApi(APIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Post checkout from Cart session",
        responses={200: "checkout details", 400: "error raised"},
    )
    def post(self, request):
        cart = request.session.get("cart")
        current_shop = request.session.get("current_shop")

        # getting the cart details to make an order
        quantities = []
        product_ids = list(cart[current_shop].keys())
        full_price = 0
        try:
            for key in cart[current_shop].keys():

                # product_ids.append(list(cart[current_shop].keys()))
                quantities.append(cart[current_shop][key]["quantity"])
                full_price += (
                    float(cart[current_shop][key]["price"])
                    * cart[current_shop][key]["quantity"]
                )
        except Exception as e:
            return Response(
                {
                    "message": "failure",
                    "error": str(e),
                    "hint": "make sure that you created cart first (cart exists for the user)",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = Product.objects.filter(id__in=product_ids)

        order = Order.objects.create(user=request.user, shop=products[0].shop)

        # making orderItem for every product
        for i in range(len(quantities)):
            OrderItem.objects.create(
                order=order, product=products[i], quantity=quantities[i]
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {"order_data": order.get_data}
        data["order_data"]["item_count"] = len(cart)

        data["order_data"]["full_price"] = str(full_price)
        data["address"] = serializer.validated_data.get("address")
        data["paying_method"] = serializer.validated_data.get("paying_method")

        if data["paying_method"] == "CASH_ON_DELIVERY":
            return Response(data, status=status.HTTP_200_OK)

        payment_attempt = PaymentAttempt.objects.create(
            mutual_reference=str(uuid.uuid4()), order=order
        )
        iframe_url = paymob.issue_payment(
            int(order.total_price.amount * 100),  # total price in cents
            payment_attempt.mutual_reference,
            items=[],
            billing_data={
                "apartment": "NA",
                "email": "NA",
                "floor": "NA",
                "first_name": "NA",
                "street": "NA",
                "building": "NA",
                "phone_number": "NA",
                "shipping_method": "NA",
                "postal_code": "NA",
                "city": "NA",
                "country": "NA",
                "last_name": "NA",
                "state": "NA",
            },
        )
        data["payment_url"] = iframe_url

        return Response(data, status=status.HTTP_200_OK)

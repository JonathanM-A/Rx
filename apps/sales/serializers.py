from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import F
from django.core.validators import MinValueValidator
from rest_framework import serializers
from .models import Cart, CartProduct, Sale, SaleFacilityProduct, Order, OrderProduct
from ..clients.models import Client
from ..facilities.models import FacilityProduct
from ..common.serializers import BaseModelSerializer


class CartProductSerializer(serializers.ModelSerializer):
    facility_product = serializers.PrimaryKeyRelatedField(
        queryset=FacilityProduct.objects.all(),
        write_only=True,
    )
    product_name = serializers.StringRelatedField(source="facility_product")
    cart = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(), write_only=True
    )

    class Meta:
        model = CartProduct
        fields = [
            "cart",
            "facility_product",
            "product_name",
            "quantity",
            "line_cost",
        ]
        read_only_fields = ["line_cost"]

    def validate_facility_product(self, obj):
        user = self.context["request"].user

        if (user.is_client and not obj.facility.has_delivery) or (
            user.is_employee and not (obj.facility == user.staff.facility)
        ):
            raise serializers.ValidationError(
                _("You do not have access to this facility.")
            )
        return obj

    def validate(self, data):
        data = super().validate(data)

        facility_product = data.get("facility_product", None)
        quantity = data.get("quantity", None)

        if quantity > facility_product.quantity:
            raise serializers.ValidationError(
                _(
                    f"Insufficient quantity of {facility_product.product.name}."
                    f"{facility_product.quantity} units remaining"
                )
            )

        return data

    def create(self, validated_data):
        facility_product = validated_data.get("facility_product", None)
        cart = validated_data.get("cart", None)
        quantity = validated_data.get("quantity", None)

        try:
            existing_product = cart.cartproduct_set.get(
                facility_product=facility_product
            )
            existing_product.quantity = F("quantity") + quantity
            existing_product.save()
            return existing_product
        except CartProduct.DoesNotExist:
            return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    cart_products = CartProductSerializer(
        source="cartproduct_set", many=True, read_only=True
    )
    products = serializers.ListField(
        child=serializers.DictField(), min_length=1, write_only=True
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), write_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "client",
            "products",
            "cart_products",
            "total_cost",
        ]
        read_only_fields = ["total_cost", "cart_products"]

    def create(self, validated_data):
        products = validated_data.pop("products")

        with transaction.atomic():
            client = validated_data.get("client")

            if hasattr(client, "cart"):
                cart = client.cart
            else:
                cart = super().create(validated_data)

            for product in products:
                product["cart"] = cart.id
                serializer = CartProductSerializer(data=product, context=self.context)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        cart.save()
        cart.refresh_from_db()
        return cart


class SaleFacilityProductSerializer(serializers.ModelSerializer):
    facility_product = serializers.PrimaryKeyRelatedField(
        queryset=FacilityProduct.objects.filter(quantity__gt=0), write_only=True
    )
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    sale = serializers.PrimaryKeyRelatedField(
        queryset=Sale.objects.all(), write_only=True
    )

    class Meta:
        model = SaleFacilityProduct
        fields = [
            "sale",
            "facility_product",
            "quantity",
            "line_cost",
        ]
        read_only_fields = ["line_cost"]

    def validate(self, data):
        data = super().validate(data)

        quantity = data.get("quantity", None)
        facility_product = data.get("facility_product", None)

        if quantity > facility_product.quantity:
            raise serializers.ValidationError(
                _(
                    f"Insufficient quantity of {facility_product.product.name}."
                    f"{facility_product.quantity} units remaining."
                )
            )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        facility_product = validated_data.get("facility_product", None)
        quantity = validated_data.get("quantity", None)

        facility_product.quantity = F("quantity") - quantity
        facility_product.save()

        return super().create(validated_data)

    def to_representation(self, instance):
        return {
            "product_name": str(instance.facility_product),
            "quantity": instance.quantity,
            "unit_cost": instance.facility_product.product.unit_selling_price,
            "line_cost": instance.line_cost,
        }


class SaleSerializer(BaseModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all()
    )
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False, write_only=True
    )
    facility_products = SaleFacilityProductSerializer(
        source="salefacilityproduct_set", many=True, read_only=True
    )

    class Meta:
        model = Sale
        fields = [
            "id"
            "created_at",
            "client",
            "order",
            "facility",
            "facility_products",
            "total_cost",
            "payment_method",
            "created_by",
        ]

        read_only_fields = [
            "id"
            "facility_products",
            "created_at",
            "total_cost",
            "facility",
            "created_by",
        ]

    def validate(self, data):
        data = super().validate(data)

        client = data.get("client")
        order = data.get("order", None)

        if order:
            data["order"] = order
        elif hasattr(client, "cart"):
            data["cart"] = client.cart
        
        return data

    @transaction.atomic()
    def create(self, validated_data):
        user = self.context["request"].user

        cart = validated_data.pop("cart", None)
        order = validated_data.pop("order", None)

        validated_data["created_by"] = user.staff
        validated_data["facility"] = user.staff.facility

        if cart:
            products = cart.cartproduct_set.all()
        else:
            products = order.orderproduct_set.all()

        sale = super().create(validated_data)

        for product in products:

            sale_product_data = {
                "facility_product": product.facility_product.id,
                "quantity": product.quantity,
                "sale": sale.id,
            }

            serializer = SaleFacilityProductSerializer(data=sale_product_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if cart:
            cart.delete()

        sale.save()
        sale.refresh_from_db()
        return sale

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["client"] = str(instance.client)
        representation["facility"] = str(instance.facility)
        representation["created_by"] = str(instance.created_by)

        return representation


class OrderProductSerializer(serializers.ModelSerializer):
    facility_product = serializers.PrimaryKeyRelatedField(
        queryset=FacilityProduct.objects.filter(quantity__gt=0), write_only=True
    )
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), write_only=True
    )

    class Meta:
        model = OrderProduct
        fields = [
            "order",
            "facility_product",
            "quantity",
            "line_cost",
        ]

    def validate(self, data):
        data = super().validate(data)

        quantity = data.get("quantity", None)
        facility_product = data.get("facility_product", None)

        if quantity > facility_product.quantity:
            raise serializers.ValidationError(
                _(
                    f"Insufficient quantity of {facility_product.product.name}."
                    f"{facility_product.quantity} units remaining."
                )
            )

        return data

    def to_representation(self, instance):
        return {
            "product_name": str(instance.facility_product),
            "quantity": instance.quantity,
            "unit_cost": instance.facility_product.product.unit_selling_price,
            "line_cost": instance.line_cost,
        }


class OrderSerializer(serializers.ModelSerializer):
    facility_products = OrderProductSerializer(
        many=True, source="orderproduct_set", required=False
        )

    class Meta:
        model = Order
        fields = [
            "id",
            "client",
            "contact",
            "location",
            "facility_products",
            "total_cost",
            "payment_method",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "client",
            "facility_products",
            "total_cost",
            "created_at",
            "id",
            "facility_products",
        ]

    def validate(self, data):
        user = self.context["request"].user

        if hasattr(user, "client"):
            data["client"] = user.client

            data = super().validate(data)
            user = self.context["request"].user

            phone_number = data.get("contact", None)

            if not phone_number:
                phone_number = user.client.phone_number
                data["phone_number"] = phone_number

        return data

    def create(self, validated_data):
        client = validated_data.get("client")

        products = client.cart.cartproduct_set.all()

        order = super().create(validated_data)

        for product in products:
            order_product_data = {
                "facility_product": product.facility_product.id,
                "quantity": product.quantity,
                "order": order.id,
                "line_cost": product.line_cost,
            }

            serializer = OrderProductSerializer(data=order_product_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        client.cart.delete()

        order.save()
        order.refresh_from_db()
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["client"] = str(instance.client)
        return representation

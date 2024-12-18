from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import (
    WarehouseProduct,
    WarehouseTransfers,
    FacilityWarehouseTransfers,
    ProductsWarehouseInbound,
    WarehouseInbound,
)
from django.utils import timezone
from ..facilities.models import Facility
from ..products.models import Product


class WarehouseProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    product_name = serializers.StringRelatedField(source="product", read_only=True)

    class Meta:
        model = WarehouseProduct
        fields = ["product", "product_name", "batch_no", "expiry_date", "quantity"]

    def validate(self, data, *args, **kwargs):
        data = super().validate(data)

        product = data.get("product", None)
        batch_no = data.get("batch_no", None)
        expiry_date = data.get("expiry_date", None)
    
        warehouse_product_instance = WarehouseProduct.objects.filter(
            product=product, batch_no=batch_no
        ).first()

        if (
            warehouse_product_instance
            and warehouse_product_instance.expiry_date != expiry_date
        ):
            raise serializers.ValidationError(
                {
                    "error": _(f"Conflicting expiry date for product {warehouse_product_instance.product.name}."
                    f"Existing expiry: {warehouse_product_instance.expiry_date}, "
                    f"New expiry: {expiry_date}")
                }
            )
        return data

    def validate_quantity(self, value):
        if int(value) < 0:
            raise serializers.ValidationError(
                _("Quantity cannot be less than 0")
            )
        return int(value)

    def validate_expiry_date(self, value):
        if value and value <= timezone.now().date():
            raise serializers.ValidationError(
                {"error": _("Expiry date must be in the future")}
            )
        return value


# Serialize warehouse product without quantity
class WarehouseProductNoQuantitySerializer(WarehouseProductSerializer):
    product_name = serializers.CharField(source="product.name")

    class Meta(WarehouseProductSerializer.Meta):
        fields = [
            field
            for field in WarehouseProductSerializer.Meta.fields
            if field != "quantity"
        ]


class FacilityWarehouseTransfersSerializer(serializers.ModelSerializer):
    warehouse_product = WarehouseProductNoQuantitySerializer()

    class Meta:
        model = FacilityWarehouseTransfers
        fields = ["warehouse_product", "quantity"]


class WarehouseTransferSerializer(serializers.ModelSerializer):
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.all(), write_only=True
    )
    facility_name = serializers.StringRelatedField(source="facility", read_only=True)
    warehouse_products = FacilityWarehouseTransfersSerializer(
        source="transfer_products", many=True
    )

    class Meta:
        model = WarehouseTransfers
        fields = [
            "id",
            "created_at",
            "transfer_no",
            "facility",
            "facility_name",
            "warehouse_products",
            "status",
        ]
        read_only_fields = ["id", "created_at"]


class ProductsWarehouseInboundSerializer(serializers.ModelSerializer):
    warehouse_product = WarehouseProductNoQuantitySerializer()

    class Meta:
        model = ProductsWarehouseInbound
        fields = ["warehouse_product", "quantity"]


class WarehouseInboundSerializer(serializers.ModelSerializer):
    warehouse_products = ProductsWarehouseInboundSerializer(
        source="inbound_products", many=True
    )

    class Meta:
        model = WarehouseInbound
        fields = "__all__"

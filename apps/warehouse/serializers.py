from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from rest_framework import serializers
from .models import (
    WarehouseProduct,
    WarehouseTransfers,
    FacilityWarehouseTransfers,
    WarehouseProductsInbound,
    WarehouseInbound,
)
from django.utils import timezone
from ..facilities.models import Facility, FacilityProduct
from ..products.models import Product


class WarehouseProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    product_name = serializers.StringRelatedField(source="product", read_only=True)

    class Meta:
        model = WarehouseProduct
        fields = ["product", "product_name", "batch_no", "expiry_date", "quantity"]

    def validate(self, data, *args, **kwargs):
        data = super().validate(data)

        product = data.get("product")
        batch_no = data.get("batch_no")
        expiry_date = data.get("expiry_date")

        warehouse_product_instance = WarehouseProduct.objects.filter(
            product=product, batch_no=batch_no
        ).first()

        if (
            warehouse_product_instance
            and warehouse_product_instance.expiry_date != expiry_date
        ):
            raise serializers.ValidationError(
                {
                    "error": _(
                        f"Conflicting expiry date for product {warehouse_product_instance.product.name}."
                        f"Existing expiry: {warehouse_product_instance.expiry_date}, "
                        f"New expiry: {expiry_date}"
                    )
                }
            )
        return data

    def validate_quantity(self, value):
        if int(value) < 0:
            raise serializers.ValidationError(_("Quantity cannot be less than 0"))
        return int(value)

    def validate_expiry_date(self, value):
        if value and value <= timezone.now().date():
            raise serializers.ValidationError(
                {"error": _("Expiry date must be in the future")}
            )
        return value

    def create(self, validated_data):
        product = validated_data["product"]
        batch_no = validated_data["batch_no"]
        expiry_date = validated_data["expiry_date"]
        quantity = validated_data["quantity"]

        with transaction.atomic():
            (
                warehouse_product,
                created,
            ) = WarehouseProduct.objects.select_for_update().get_or_create(
                product=product,
                batch_no=batch_no,
                expiry_date=expiry_date,
            )

            warehouse_product.quantity = F("quantity") + quantity
            warehouse_product.save()

            warehouse_product.refresh_from_db()

        return warehouse_product


# Serialize warehouse product without quantity
class WarehouseProductNoQuantitySerializer(WarehouseProductSerializer):

    class Meta(WarehouseProductSerializer.Meta):
        fields = [
            field
            for field in WarehouseProductSerializer.Meta.fields
            if field != "quantity"
        ]


class FacilityWarehouseTransfersSerializer(serializers.ModelSerializer):
    transfer = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseTransfers.objects.all(), write_only=True
    )
    warehouse_product_read_only = WarehouseProductNoQuantitySerializer(
        source="warehouse_product", read_only=True
    )
    warehouse_product = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseProduct.objects.all(), write_only=True
    )
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = FacilityWarehouseTransfers
        fields = [
            "warehouse_product_read_only",
            "warehouse_product",
            "transfer",
            "quantity",
        ]


class WarehouseTransferSerializer(serializers.ModelSerializer):
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.all(), write_only=True
    )
    facility_name = serializers.StringRelatedField(source="facility", read_only=True)
    products = serializers.ListField(
        child=serializers.DictField(allow_empty=False), min_length=1, write_only=True
    )
    transfer_products = FacilityWarehouseTransfersSerializer(
         many=True, read_only=True
    )

    class Meta:
        model = WarehouseTransfers
        fields = [
            "id",
            "created_at",
            "transfer_no",
            "facility",
            "facility_name",
            "transfer_products",
            "products",
            "status",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_products(self, products):
        for product in products:
            quantity = product["quantity"]
            product_id = product["product"]

            if not all([quantity, product_id]):
                raise serializers.ValidationError(
                    _("'Quantity' and 'Product' are required")
                )

            if not (isinstance(quantity, int) and quantity > 0):
                raise serializers.ValidationError(
                    _("Quantity must be an intger greater than 0")
                )

            try:
                product_instance = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    _(
                        f"The product with if {product_id} is not available the formulary."
                    )
                )
            product["product"] = product_instance

            batches = WarehouseProduct.objects.filter(
                product=product_id, quantity__gt=0
            ).order_by("-expiry_date")

            result = batches.aggregate(
                total_quantity=Sum("quantity"),
            )
            total_product_quantity = result["total_quantity"]

            if total_product_quantity < quantity:
                raise serializers.ValidationError(
                    _(
                        f"Insufficient stock of {product.name}. "
                        f"{total_product_quantity} packs available."
                    )
                )

        return products

    def create(self, validated_data):
        with transaction.atomic():

            facility = validated_data["facility"]
            products = validated_data.pop("products")
            transfer = super().create(validated_data)

            for product in products:
                product_instance = product["product"]
                quantity = product["quantity"]

                batches = (
                    WarehouseProduct.objects.select_for_update()
                    .filter(product=product_instance, quantity__gt=0)
                    .order_by("-expiry_date")
                )

                for batch in batches:
                    if batch.quantity >= quantity:
                        batch.quantity = F("quantity") - quantity
                        batch.save()

                        facility_item, created = FacilityProduct.objects.get_or_create(
                            facility=facility, product=product_instance
                        )
                        facility_item.quantity = F("quantity") + quantity
                        facility_item.save()

                        transfer_data = {
                            "transfer": transfer.id,
                            "warehouse_product": batch.id,
                            "quantity": quantity,
                        }

                        serializer = FacilityWarehouseTransfersSerializer(
                            data=transfer_data
                        )
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        break
                    else:
                        quantity -= batch.quantity
                        facility_item, created = FacilityProduct.objects.get_or_create(
                            facility=facility, product=product_instance
                        )
                        facility_item.quantity = F("quantity") + batch.quantity
                        facility_item.save()

                        transfer_data = {
                            "transfer": transfer.id,
                            "warehouse_product": batch.id,
                            "quantity": batch.quantity,
                        }
                        serializer = FacilityWarehouseTransfersSerializer(
                            data=transfer_data
                        )
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        batch.quantity = 0
                        batch.save()

        transfer.refresh_from_db()
        return transfer


class WarehouseProductsInboundSerializer(serializers.ModelSerializer):
    warehouse_product = WarehouseProductNoQuantitySerializer(read_only=True)
    inbound = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseInbound.objects.all(), write_only=True
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    batch_no = serializers.CharField(write_only=True)
    expiry_date = serializers.DateField(write_only=True)
    quantity = serializers.IntegerField()

    class Meta:
        model = WarehouseProductsInbound
        fields = [
            "warehouse_product",
            "inbound",
            "product",
            "batch_no",
            "expiry_date",
            "quantity",
        ]

    def create(self, validated_data):
        product = validated_data.pop("product")
        batch_no = validated_data.pop("batch_no")
        expiry_date = validated_data.pop("expiry_date")
        quantity = validated_data["quantity"]

        serializer = WarehouseProductSerializer(
            data={
                "product": product.id,
                "batch_no": batch_no,
                "expiry_date": expiry_date,
                "quantity": quantity,
            }
        )

        serializer.is_valid(raise_exception=True)
        warehouse_product = serializer.save()

        validated_data["warehouse_product"] = warehouse_product

        inbound_warehouse_product = super().create(validated_data)

        return inbound_warehouse_product


class WarehouseInboundSerializer(serializers.ModelSerializer):
    supplier = serializers.CharField()
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    products = serializers.ListField(
        child=serializers.DictField(), min_length=1, write_only=True
    )
    inbound_products = WarehouseProductsInboundSerializer(many=True, read_only=True)

    class Meta:
        model = WarehouseInbound
        fields = [
            "id",
            "created_at",
            "supplier",
            "invoice_no",
            "invoice_date",
            "products",
            "inbound_products",
        ]
        read_only = ["id", "created_at"]

    def create(self, validated_data):
        with transaction.atomic():
            products = validated_data.pop("products")
            inbound = super().create(validated_data)

            for product in products:
                product["inbound"] = inbound.id
                serializer = WarehouseProductsInboundSerializer(data=product)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        inbound.refresh_from_db()
        return inbound

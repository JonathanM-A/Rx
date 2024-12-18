from django.utils.translation import gettext_lazy as _
from django.db.models import F, Sum
from django.db import transaction
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import ModelViewSet

from .models import (
    WarehouseProduct,
    WarehouseTransfers,
    FacilityWarehouseTransfers,
    WarehouseInbound,
    ProductsWarehouseInbound,
)
from ..users.permissions import IsWarehouse
from .serializers import (
    WarehouseInboundSerializer,
    WarehouseProductSerializer,
    WarehouseTransferSerializer,
    FacilityWarehouseTransfersSerializer,
)
from ..products.models import Product
from ..facilities.models import Facility, FacilityProduct
from ..facilities.serializers import FacilityProductSerializer


class WarehouseProductView(ListAPIView):
    permission_classes = [IsWarehouse]
    queryset = WarehouseProduct.objects.all().select_related("product")
    serializer_class = WarehouseProductSerializer
    search_fields = ["product__name", "batch_no"]
    filterset_fields = ["expiry_date"]


class WarehouseInboundView(ModelViewSet):
    permission_classes = [IsWarehouse]
    serializer_class = WarehouseInboundSerializer
    queryset = WarehouseInbound.objects.all().order_by("-created_at")
    filterset_fields = [
        "supplier",
        "invoice_no",
        "invoice_date",
        "created_at",
    ]
    lookup_field = "id"
    http_method_names = ["post", "get"]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):

        supplier = request.data.get("supplier", None)
        invoice_no = request.data.get("invoice_no", None)
        invoice_date = request.data.get("invoice_date", None)
        products = request.data.get("products", None)

        if not all([supplier, invoice_no, invoice_date]):
            raise ValidationError(
                _(
                    "Each item must have a 'product id', 'batch no', 'expiry date' and 'quantity'."
                )
            )

        if not products or not isinstance(products, list):
            return ValidationError(_("A valid list of products must be provided"))

        inbound_instance = WarehouseInbound.objects.create(
            supplier=supplier, invoice_no=invoice_no, invoice_date=invoice_date
        )

        for product in products:
            serializer = WarehouseProductSerializer(data=product)
            if serializer.is_valid(raise_exception=True):

                product_id = product.get("product", None)
                batch_no = product.get("batch_no", None)
                expiry_date = product.get("expiry_date", None)
                quantity = product.get("quantity", None)

                product_instance = Product.objects.get(id=product_id)

                warehouse_product, created = WarehouseProduct.objects.get_or_create(
                    product=product_instance,
                    batch_no=batch_no,
                    expiry_date=expiry_date,
                )
                warehouse_product.quantity = F("quantity") + quantity
                warehouse_product.save()

                ProductsWarehouseInbound.objects.create(
                    inbound=inbound_instance,
                    warehouse_product=warehouse_product,
                    quantity=quantity,
                )
        serializer = WarehouseInboundSerializer(inbound_instance)
        return Response(
            {
                "message": _("Inbound successful"),
                "inbound_id": inbound_instance.id,
                "inbound": serializer.data,
            },
            status=201,
        )


class WarehouseTransferView(ModelViewSet):
    permission_classes = [IsWarehouse]
    serializer_class = WarehouseTransferSerializer
    queryset = WarehouseTransfers.objects.none()
    http_method_names = ["get", "post"]
    filterset_fields = ["transfer_no", "facility__name", "created_at"]

    def get_queryset(self):
        user = self.request.user

        if not user.facility:
            queryset = (
                WarehouseTransfers.objects.all()
                .select_related("facility")
                .prefetch_related("transfer_products")
                .order_by("-created_at")
            )
        else:
            queryset = (
                WarehouseTransfers.objects.filter(facility=user.facility)
                .select_related("facility")
                .prefetch_related("transfer_products")
                .order_by(-"created_at")
            )
        return queryset

    @transaction.atomic()
    def post(self, request, *args, **kwargs):

        facility_id = request.data.get("facility", None)
        products = request.data.get("products", None)

        if not isinstance(products, list):
            raise ValidationError(_("A valid list of products must be provided."))

        facility = Facility.objects.filter(id=facility_id).first()
        if facility:
            transfer_instance = WarehouseTransfers.objects.create(facility=facility)
        else:
            raise NotFound(_("A valid facility must be provided."))

        for product in products:
            product["facility"] = facility_id
            quantity = product.get("quantity", None)
            serializer = FacilityProductSerializer(data=product)

            if serializer.is_valid(raise_exception=True):
                product_id = product.get("product", None)
                product_instance = Product.objects.prefetch_related("warehouse").get(
                    id=product_id
                )

                batches = product_instance.warehouse.filter(quantity__gt=0).order_by(
                    "-expiry_date"
                )

                if batches.count() == 0:
                    raise NotFound(
                        _(f"{product_instance.name} is not available in the ware")
                    )

                total_product_quantity = batches.aggregate(
                    total_quantity=Sum("quantity")
                )["total_quantity"]

                if total_product_quantity < quantity:
                    raise ValidationError(
                        _(
                            f"Insufficient stock of {product.name}. {total_product_quantity} packs available"
                        )
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

                        FacilityWarehouseTransfers.objects.create(
                            transfer=transfer_instance,
                            warehouse_product=batch,
                            quantity=quantity,
                        )
                        break
                    else:
                        quantity -= batch.quantity
                        facility_item, created = FacilityProduct.objects.create(
                            facility=facility, product=product_instance
                        )
                        facility_item.quantity = F("quantity") + batch.quantity
                        facility_item.save()

                        FacilityWarehouseTransfers.objects.create(
                            transfer=transfer_instance,
                            warehouse_product=batch,
                            quantity=batch.quantity,
                        )
                        batch.quantity = 0
                        batch.save()

        supplied_products = FacilityWarehouseTransfers.objects.filter(
            transfer=transfer_instance.id
        )
        serializer = FacilityWarehouseTransfersSerializer(supplied_products, many=True)
        return Response(
            {
                "message": "Transfer successful",
                "transfer_id": transfer_instance.id,
                "products": serializer.data,
            },
            status=201,
        )

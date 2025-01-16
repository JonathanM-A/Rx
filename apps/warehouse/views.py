from django.utils.translation import gettext_lazy as _
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from .models import (
    WarehouseProduct,
    WarehouseTransfers,
    WarehouseInbound,
)
from ..staff.permissions import IsWarehouse, IsManagement
from .serializers import (
    WarehouseInboundSerializer,
    WarehouseProductSerializer,
    WarehouseTransferSerializer,
)


class WarehouseProductView(ListAPIView):
    permission_classes = [IsWarehouse|IsManagement]
    queryset = WarehouseProduct.objects.all().select_related("product")
    serializer_class = WarehouseProductSerializer
    search_fields = ["product__name", "batch_no"]
    filterset_fields = ["expiry_date"]

class WarehouseInboundView(ModelViewSet):
    permission_classes = [IsWarehouse|IsManagement]
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


class WarehouseTransferView(ModelViewSet):
    permission_classes = [IsWarehouse|IsManagement]
    serializer_class = WarehouseTransferSerializer
    queryset = WarehouseTransfers.objects.all()
    http_method_names = ["get", "post"]
    filterset_fields = ["transfer_no", "facility__name", "created_at"]

    def get_queryset(self):
        user = self.request.user.staff

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
                .order_by("-created_at")
            )
        return queryset

    
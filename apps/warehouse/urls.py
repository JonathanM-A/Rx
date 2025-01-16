from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseInboundView,
    WarehouseProductView,
    WarehouseTransferView,
)

router = DefaultRouter()
router.register(r"inbound", WarehouseInboundView)
router.register(r"transfer", WarehouseTransferView)

urlpatterns = [
    path("inventory", WarehouseProductView.as_view(), name="warehouse_product"),
    path("", include(router.urls)),
]

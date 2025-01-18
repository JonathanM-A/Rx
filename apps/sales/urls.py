from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, SaleViewSet, OrderViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r"sale", SaleViewSet)
router.register(r"cart", CartViewSet)
router.register(r"order", OrderViewSet)
router.register(r"prescription", PrescriptionViewSet)

urlpatterns = [
    path("", include(router.urls))
]

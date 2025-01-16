from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, SaleViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"sale", SaleViewSet)
router.register(r"cart", CartViewSet)
router.register(r"order", OrderViewSet)

urlpatterns = [
    path("", include(router.urls))
]

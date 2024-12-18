from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, MakeSaleView, CartView, ClientSaleHistory

router = DefaultRouter()
router.register("sales", SaleViewSet)

urlpatterns = [
    path("cart/<str:pk>/", CartView.as_view(), name="cart"),
    path("sales/create/<str:pk>/", MakeSaleView.as_view(), name="make_sale"),
    path("sales/history/<str:pk>/", ClientSaleHistory.as_view(), name="sale_history"),
    path("", include(router.urls)),
]

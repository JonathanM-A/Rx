from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacilityProductsView, FacilityViewSet


router = DefaultRouter()
router.register(r"facility", FacilityViewSet)

app_name = "facilities"
urlpatterns = [
    path("inventory/", FacilityProductsView.as_view(), name="facility_inventory"),
    path("", include(router.urls)),
]

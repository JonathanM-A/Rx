from django.urls import path, include
from .views import ClientViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"client", ClientViewSet)

urlpatterns = [
    path("", include(router.urls))
]

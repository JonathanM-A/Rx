from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.db.models import F
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Facility, FacilityProduct
from .serializers import FacilitySerializer, FacilityProductSerializer
from ..users.permissions import IsSuperUser, IsManager
from ..users.serializers import UserSerializer
from ..users.models import User


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all().prefetch_related("staff")
    serializer_class = FacilitySerializer
    permission_classes = [IsSuperUser | IsManager]
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ["put", "delete"]
    ]
    lookup_field = "slug"


class FacilityProductsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FacilityProductSerializer
    queryset = FacilityProduct.objects.none()
    filterset_fields = ["facility__name"]
    search_fields = ["product__generic_name", "product__brand_name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_management:
            return FacilityProduct.objects.all().select_related("product")
        elif user.facility:
            return FacilityProduct.objects.filter(facility=user.facility)
        return super().get_queryset()


# Request a transfer of product from one facility to another
# View transfer requests with option to accept or reject

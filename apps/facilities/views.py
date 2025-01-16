from django.utils.translation import gettext_lazy as _
from django.db.models import F
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from .models import Facility, FacilityProduct
from .serializers import FacilitySerializer, FacilityProductSerializer
from ..staff.permissions import IsManagement, IsRetail
from ..users.permissions import IsClient


class FacilityViewSet(ModelViewSet):
    queryset = Facility.objects.all().prefetch_related("staff")
    serializer_class = FacilitySerializer
    permission_classes = [IsManagement]
    http_method_names = [
        m for m in ModelViewSet.http_method_names if m not in ["put", "delete"]
    ]
    lookup_field = "slug"


class FacilityProductsView(ListAPIView):
    permission_classes = [IsRetail | IsManagement | IsClient]
    serializer_class = FacilityProductSerializer
    queryset = FacilityProduct.objects.all()
    filterset_fields = ["facility__name"]
    search_fields = ["product__generic_name", "product__brand_name"]

    def get_queryset(self):
        if not hasattr(self.request.user, "staff"):
            queryset = (
                FacilityProduct.objects.filter(facility__has_delivery=True)
                .select_related("product")
                .order_by("product__generic_name")
            )
        else:
            user = self.request.user.staff
        if user.is_management:
            queryset = (
                FacilityProduct.objects.all()
                .select_related("product")
                .order_by("product__generic_name")
            )
        elif user.facility:
            queryset =(
                FacilityProduct.objects.filter(facility=user.facility).
                order_by("product__generic_name")
            )
        return queryset

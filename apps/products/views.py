from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from ..users.permissions import IsAdminUser, IsManager


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("generic_name")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser | IsManager]
    search_fields = ["generic_name", "brand_name"]

from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer
from ..staff.permissions import IsAdmin, IsManagement



class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdmin|IsManagement]
    queryset = Product.objects.all().order_by("generic_name")
    serializer_class = ProductSerializer
    search_fields = ["generic_name", "brand_name"]
    http_method_names = [m for m in ModelViewSet.http_method_names if m != "delete"]

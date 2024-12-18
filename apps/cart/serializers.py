from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Sale, SaleProduct
from ..clients.models import Client
from ..facilities.models import FacilityProduct, Facility
from ..users.models import User


class SaleProductSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(
        queryset=Sale.objects.all(), write_only=True
    )
    facility_product = serializers.PrimaryKeyRelatedField(
        queryset=FacilityProduct.objects.none(), write_only=True
    )
    product = serializers.StringRelatedField(source="facility_product", read_only=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = SaleProduct
        fields = ["sale", "facility_product", "product", "quantity", "cost"]

    def get_cost(self, obj):
        return obj.line_cost


class SaleSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), write_only=True
    )
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.all(), write_only=True
    )
    facility_products = SaleProductSerializer(many=True, source="saleproduct_set")
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(facility__isnull=False), write_only=True
    )

    total_cost = serializers.SerializerMethodField(read_only=True)
    client_name = serializers.StringRelatedField(source="client", read_only=True)
    facility_name = serializers.StringRelatedField(source="facility", read_only=True)
    vendor = serializers.StringRelatedField(source="created_by", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "client",
            "client_name",
            "facility",
            "facility_name",
            "facility_products",
            "total_cost",
            "created_by",
            "vendor",
            "created_at",
        ]

    def get_total_cost(self, obj):
        return obj.total_cost

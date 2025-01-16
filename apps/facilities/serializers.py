from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Facility, FacilityProduct
from ..common.serializers import BaseModelSerializer
from ..products.models import Product


class FacilitySerializer(BaseModelSerializer):

    class Meta:
        model = Facility

        fields = [
            "name",
            "city",
            "region",
            "country",
            "slug",
        ]

    def validate(self, data):
        name = data.get("name")
        city = data.get("city")
        region = data.get("region")

        if Facility.objects.filter(
            name__iexact=name, city__iexact=city, region__iexact=region
        ).exists():
            raise serializers.ValidationError(
                {
                    "error": _(f"A facility with name {name} already exists in {city}, {region}.")
                }
            )
        return data


class FacilityProductSerializer(serializers.ModelSerializer):
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.all(), write_only=True
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    product_name = serializers.StringRelatedField(source="product", read_only=True)
    selling_price = serializers.DecimalField(source="product.unit_selling_price", max_digits=7, decimal_places=2)
    image = serializers.ImageField(source="product.image")

    class Meta:
        model = FacilityProduct
        fields = ["facility", "product", "product_name","quantity", "selling_price", "image"]
        read_only_fields = ["product_name", "selling_price", "image"]

    def validate_quantity(self, value):
        if int(value) < 0:
            raise serializers.ValidationError(
                _("Quantity cannot be less than 0")
            )
        return int(value)
    
    def validate(self, attrs):
        print("HERE", attrs)
        return super().validate(attrs)

class FacilityProductSerializerNoQuantity(FacilityProductSerializer):
    class Meta(FacilityProductSerializer.Meta):
        fields = [
            field for field in FacilityProductSerializer.Meta.fields if field != "quantity"
        ]
        
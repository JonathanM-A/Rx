from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "generic_name",
            "brand_name",
            "form",
            "strength",
            "pack_size",
            "cost_price_pack",
            "selling_price_pack",
        ]

    def validate(self, data):
        data = super().validate(data)

        generic_name = data.get("generic_name")
        brand_name = data.get("brand_name")
        form = data.get("form")
        strength = data.get("strength")
        pack_size = data.get("pack_size")
        cost_price = data.get("cost_price_pack")
        selling_price = data.get("selling_price_pack")

        if Product.objects.filter(
            generic_name=generic_name,
            brand_name=brand_name,
            form=form,
            strength=strength,
            pack_size=pack_size,
        ).exists():
            raise serializers.ValidationError({"error": "This product already exists"})

        if cost_price > selling_price:
            raise serializers.ValidationError(
                {
                    "error": "The product selling price must be greater that the cost price."
                }
            )

        return data

from django.db import models
from django.core.validators import MinValueValidator
from ..common.models import BaseModel


class Product(BaseModel):
    generic_name = models.CharField(null=False, blank=False)
    brand_name = models.CharField(null=True, blank=False)
    form = models.CharField(null=False, blank=False)  # Consider adding choices
    strength = models.CharField(null=False, blank=False)
    pack_size = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(0)]
    )
    cost_price_pack = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
    )
    selling_price_pack = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField(null=True, blank=True)

    class Meta:
        unique_together = [
            "generic_name",
            "brand_name",
            "pack_size",
            "form",
            "strength",
        ]

    def __str__(self):
        return self.name

    @property
    def name(self):
        parts = [self.generic_name]
        if self.brand_name:
            parts.append(f"({self.brand_name})")
        parts.extend([self.strength, self.form.title(), f"x{self.pack_size}"])
        return " ".join(parts)

    @property
    def unit_selling_price(self):
        return round((self.selling_price_pack / self.pack_size), 2)

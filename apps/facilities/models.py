import uuid
from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from ..common.models import BaseModel
from ..products.models import Product


class Facility(BaseModel):

    name = models.CharField(null=False, blank=False)
    city = models.CharField(null=False, blank=False)
    region = models.CharField(null=False, blank=False)
    country = CountryField(null=False, blank=False)
    has_delivery = models.BooleanField(blank=False, default=True)
    slug = models.CharField(unique=True, null=True, blank=False)
    products = models.ManyToManyField(
        Product, through="FacilityProduct", related_name="facilities"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            combined_string = f"{self.name}-{self.city}"
            self.slug = slugify(combined_string)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "facility"
        verbose_name_plural = "facilities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.city}"


@receiver(pre_save, sender=Facility)
def facility_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        base_slug = slugify(f"{instance.name}-{instance.city}")
        slug = base_slug
        num = 1
        while Facility.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        instance.slug = slug


class FacilityProduct(BaseModel):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        default=0, null=False, blank=False, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return str(self.product)

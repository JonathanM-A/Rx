from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from ..clients.models import Client
from ..staff.models import Staff
from ..facilities.models import FacilityProduct, Facility
from ..common.models import BaseModel
from ..common.validators import phone_validator, location_validator


PAYMENT_METHOD = [
    ("insurance", "Insurance"),
    ("out of pocket", "Out of pocket"),
    ("online payment", "Online Payment"),
    ("no cost", "Provide at no cost"),
]


class Cart(BaseModel):
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name="cart"
    )
    facility_products = models.ManyToManyField(FacilityProduct, through="CartProduct")
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=True
    )

    def save(self, *args, **kwargs):
        if self.facility_products:
            self.total_cost = sum(
                product.line_cost for product in self.cartproduct_set.all()
            )
        return super().save(*args, **kwargs)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    facility_product = models.ForeignKey(FacilityProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, validators=[MinValueValidator(1)])
    line_cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, default=0.00
    )

    def save(self, *args, **kwargs):
        unit_selling_price = self.facility_product.product.unit_selling_price
        self.line_cost = self.quantity * unit_selling_price
        return super().save(*args, **kwargs)


class Sale(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    facility_products = models.ManyToManyField(
        FacilityProduct, through="SaleFacilityProduct"
    )
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, default=0.00
    )
    payment_method = models.CharField(choices=PAYMENT_METHOD, blank=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                super().save(*args, **kwargs)

            self.total_cost = sum(
                facility_product.line_cost
                for facility_product in self.salefacilityproduct_set.all()
            )
            return super().save(update_fields=["total_cost"])


class SaleFacilityProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    facility_product = models.ForeignKey(FacilityProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, validators=[MinValueValidator(1)])
    line_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

    def save(self, *args, **kwargs):
        unit_selling_price = self.facility_product.product.unit_selling_price
        self.line_cost = self.quantity * unit_selling_price
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.facility_product.quantity = models.F("quantity") + self.quantity
            self.facility_product.save()

            return super().delete(*args, **kwargs)


class Order(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    IMMUTABLE_FIELDS = ["client", "contact", "location"]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    contact = models.CharField(null=True, blank=True, validators=[phone_validator])
    facility_products = models.ManyToManyField(
        FacilityProduct, through="OrderProduct"
    )
    location = models.URLField(blank=False, validators=[location_validator])
    status = models.CharField(choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(choices=PAYMENT_METHOD, blank=False)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, default=0.00
    )

    def clean(self):
        super().clean()
        if self.pk:
            try:
                existing = Order.objects.get(pk=self.pk)

                for field_name in self.IMMUTABLE_FIELDS:
                    if getattr(self, field_name) != getattr(existing, field_name):
                        raise ValidationError(
                            _(f"The field {field_name} is immutable and cannot be updated")
                        )
            except Order.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.facility_products:
            self.total_cost = sum(
                product.line_cost for product in self.orderproduct_set.all()
            )
        return super().save(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    facility_product = models.ForeignKey(FacilityProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, validators=[MinValueValidator(1)])
    line_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

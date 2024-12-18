from django.db import models
from django.core.validators import MinValueValidator
from ..facilities.models import FacilityProduct
from ..clients.models import Client
from ..facilities.models import Facility
from ..common.models import BaseModel
from ..users.models import User


class Sale(BaseModel):
    PAYMENT_METHOD = [
        ("insurance", "Insurance"),
        ("corporate", "Corporate"),
        ("out_of_pocket", "Out of Pocket"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    facility_products = models.ManyToManyField(FacilityProduct, through="SaleProduct")
    payment_method = models.CharField(choices=PAYMENT_METHOD, null=False, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )

    @property
    def total_cost(self, *args, **kwargs):
        return sum(
            sale_product.line_total for sale_product in self.saleproduct_set.all()
        )


class SaleProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=False, blank=False)
    facility_product = models.ForeignKey(
        FacilityProduct, on_delete=models.CASCADE, null=False, blank=False
    )
    quantity = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(1)]
    )

    @property
    def line_total(self, *args, **kwargs):
        unit_selling_price = self.facility_product.product.unit_selling_price
        return self.quantity * unit_selling_price

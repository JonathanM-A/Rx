from django.db import models
from ..products.models import Product
from ..facilities.models import Facility
from ..common.models import BaseModel


class WarehouseProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="warehouse"
    )
    batch_no = models.CharField(max_length=20, blank=False, null=False)
    expiry_date = models.DateField(blank=False, null=False)
    quantity = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self) -> str:
        return (
            f"{self.product.name}, Batch No.: {self.batch_no}, "
            f"Expiry: {self.expiry_date}, Quantity: {self.quantity}"
        )


class WarehouseTransfers(BaseModel):
    STATUS_CHOICES = [
        ("STATUS_PENDING", "Pending"),
        ("STATUS_IN_PROGRESS", "In Progress"),
        ("STATUS_COMPLETED", "Completed"),
    ]

    transfer_no = models.CharField(
        max_length=5, editable=False, null=False, blank=False, unique=True
    )
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="transfers"
    )
    warehouse_product = models.ManyToManyField(
        WarehouseProduct, through="FacilityWarehouseTransfers", related_name="transfers"
    )
    status = models.CharField(
        default="STATUS_PENDING", choices=STATUS_CHOICES, null=False, blank=False
    )

    def save(self, *args, **kwargs):
        if not self.transfer_no:
            last_transfer = WarehouseTransfers.objects.order_by("-transfer_no").first()
            if last_transfer:
                new_id = int(last_transfer.transfer_no) + 1
            else:
                new_id = 1
            self.transfer_no = f"{new_id:05}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Transfer No.: {self.transfer_no}, Date: {self.created_at}"


# Custom Intermediate Table
class FacilityWarehouseTransfers(models.Model):
    transfer = models.ForeignKey(
        WarehouseTransfers, on_delete=models.CASCADE, related_name="transfer_products"
    )
    warehouse_product = models.ForeignKey(WarehouseProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False)


class WarehouseInbound(BaseModel):
    supplier = models.CharField(null=False, blank=False)
    invoice_no = models.CharField(null=False, blank=False)
    invoice_date = models.DateField(null=False, blank=False)
    warehouse_products = models.ManyToManyField(
        WarehouseProduct, through="ProductsWarehouseInbound",
    )

# Custom Intermediate Table
class ProductsWarehouseInbound(models.Model):
    inbound = models.ForeignKey(WarehouseInbound, on_delete=models.CASCADE, related_name="inbound_products")
    warehouse_product = models.ForeignKey(WarehouseProduct, on_delete=models.CASCADE, related_name="inbound_products")
    quantity = models.IntegerField(null=False, blank=False)

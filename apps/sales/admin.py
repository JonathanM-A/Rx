from django.contrib import admin
from .models import (
    Cart,
    CartProduct,
    Order,
    OrderProduct,
    Sale,
    SaleFacilityProduct,
    Prescription,
)

# Register your models here.

admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Sale)
admin.site.register(SaleFacilityProduct)
admin.site.register(Prescription)

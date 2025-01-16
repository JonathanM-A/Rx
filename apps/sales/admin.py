from django.contrib import admin
from .models import Cart, CartProduct, Order
# Register your models here.

admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)

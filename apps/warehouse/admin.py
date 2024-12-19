from django.contrib import admin
from .models import WarehouseProduct, WarehouseTransfers, WarehouseInbound


admin.site.register(WarehouseProduct)
admin.site.register(WarehouseTransfers)
admin.site.register(WarehouseInbound)
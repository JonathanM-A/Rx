# Generated by Django 5.1.3 on 2024-12-31 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_rename_products_warehouseinbound_warehouse_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseproduct',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-01 15:09

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilitywarehousetransfers',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_products', to='warehouse.warehousetransfers'),
        ),
        migrations.CreateModel(
            name='ProductsWarehouseInbound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('warehouse_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_products', to='warehouse.warehouseproduct')),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseInbound',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('supplier', models.CharField()),
                ('invoice_no', models.CharField()),
                ('invoice_date', models.DateField()),
                ('warehouse_products', models.ManyToManyField(through='warehouse.ProductsWarehouseInbound', to='warehouse.warehouseproduct')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='productswarehouseinbound',
            name='inbound',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouseinbound'),
        ),
    ]
# Generated by Django 5.1.3 on 2024-11-30 19:07

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facilities', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarehouseProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_no', models.CharField(max_length=20)),
                ('expiry_date', models.DateField()),
                ('quantity', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='FacilityWarehouseTransfers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('warehouse_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouseproduct')),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseTransfers',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('transfer_no', models.CharField(editable=False, max_length=5, unique=True)),
                ('status', models.CharField(choices=[('STATUS_PENDING', 'Pending'), ('STATUS_IN_PROGRESS', 'In Progress'), ('STATUS_COMPLETED', 'Completed')], default='STATUS_PENDING')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='facilities.facility')),
                ('warehouse_product', models.ManyToManyField(related_name='transfers', through='warehouse.FacilityWarehouseTransfers', to='warehouse.warehouseproduct')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='facilitywarehousetransfers',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehousetransfers'),
        ),
    ]

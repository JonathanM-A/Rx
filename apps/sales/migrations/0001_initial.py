# Generated by Django 5.1.3 on 2025-01-15 20:25

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0015_insurancecorporatecompany_and_more'),
        ('facilities', '0008_rename_uuid_facilityproduct_id'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='clients.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('line_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.cart')),
                ('facility_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facilities.facilityproduct')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(through='sales.CartProduct', to='facilities.facilityproduct'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('contact', models.CharField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('location', models.URLField(validators=[django.core.validators.RegexValidator(message='Location must be a Google Maps link.', regex='^^https:\\/\\/maps\\.app\\.goo\\.gl\\/[a-zA-Z0-9]+$')])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')),
                ('payment_method', models.CharField(choices=[('insurance', 'Insurance'), ('out_of_pocket', 'Out of pocket'), ('online_payment', 'Online Payment'), ('no_cost', 'Provide at no cost')])),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('line_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('facility_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facilities.facilityproduct')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='facility_products',
            field=models.ManyToManyField(through='sales.OrderProducts', to='facilities.facilityproduct'),
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_method', models.CharField(choices=[('insurance', 'Insurance'), ('out_of_pocket', 'Out of pocket'), ('online_payment', 'Online Payment'), ('no_cost', 'Provide at no cost')])),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facilities.facility')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SaleFacilityProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('line_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('facility_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facilities.facilityproduct')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.sale')),
            ],
        ),
        migrations.AddField(
            model_name='sale',
            name='facility_products',
            field=models.ManyToManyField(through='sales.SaleFacilityProduct', to='facilities.facilityproduct'),
        ),
    ]

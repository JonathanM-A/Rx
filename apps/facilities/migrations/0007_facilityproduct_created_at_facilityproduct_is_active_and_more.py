# Generated by Django 5.1.3 on 2025-01-15 19:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0006_auto_20250115_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityproduct',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='created_at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facilityproduct',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='facilityproduct',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='modified_at'),
        ),
    ]
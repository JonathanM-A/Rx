# Generated by Django 5.1.3 on 2025-01-15 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='products',
            new_name='facility_products',
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-17 20:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0007_client_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='age',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
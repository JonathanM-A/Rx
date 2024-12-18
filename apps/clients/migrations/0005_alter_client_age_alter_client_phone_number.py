# Generated by Django 5.1.3 on 2024-12-09 13:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_alter_client_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='age',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=models.CharField(null=True, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$'), django.core.validators.MinLengthValidator(10)]),
        ),
    ]

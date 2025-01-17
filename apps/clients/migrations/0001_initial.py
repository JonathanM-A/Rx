# Generated by Django 5.1.3 on 2024-12-06 20:02

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('first_name', models.CharField()),
                ('last_name', models.CharField()),
                ('age', models.IntegerField(validators=[django.core.validators.MinValueValidator(18)])),
                ('phone_number', models.CharField(unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$'), django.core.validators.MinLengthValidator(10)])),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])),
                ('is_insurance', models.BooleanField(default=False)),
                ('insurance_company', models.CharField(choices=[('acacia', 'Acacia Health Insurance'), ('apex', 'Apex Health Insurance'), ('glico_health', 'Glico Health Insurane'), ('glico_tpa', 'Glico TPA')], null=True)),
                ('is_corporate', models.BooleanField(default=False)),
                ('corporate_company', models.CharField(choices=[('vivo', 'Vivo Energy Limited'), ('mtn', 'MTN Ghana'), ('stanbic_bank', 'Stanbic Bank Ghana')], null=True)),
                ('insurance_corporate_id', models.CharField(null=True)),
                ('parent_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clients.client')),
                ('parent_facility', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facilities.facility')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-25 18:13

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0014_clientoutstandingtoken'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InsuranceCorporateCompany',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modified_at')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(unique=True)),
                ('is_insurance', models.BooleanField()),
                ('is_corporate', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='clientoutstandingtoken',
            name='client',
        ),
        migrations.RemoveField(
            model_name='clientoutstandingtoken',
            name='outstandingtoken_ptr',
        ),
        migrations.DeleteModel(
            name='PasswordResetLog',
        ),
        migrations.RemoveField(
            model_name='client',
            name='corporate_company',
        ),
        migrations.RemoveField(
            model_name='client',
            name='email',
        ),
        migrations.RemoveField(
            model_name='client',
            name='insurance_company',
        ),
        migrations.RemoveField(
            model_name='client',
            name='is_client',
        ),
        migrations.RemoveField(
            model_name='client',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='client',
            name='password',
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(limit_choices_to={'is_client': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='client',
            name='parent_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client'),
        ),
        migrations.AddField(
            model_name='client',
            name='insurance_corporate_company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.insurancecorporatecompany'),
        ),
        migrations.DeleteModel(
            name='ClientOutstandingToken',
        ),
    ]

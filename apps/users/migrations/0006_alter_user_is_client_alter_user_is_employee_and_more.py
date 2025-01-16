# Generated by Django 5.1.3 on 2024-12-28 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_options_remove_user_facility_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_client',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_employee',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
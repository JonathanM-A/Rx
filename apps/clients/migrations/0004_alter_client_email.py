# Generated by Django 5.1.3 on 2024-12-08 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_remove_client_parent_facility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]

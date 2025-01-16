# Generated by Django 5.1.3 on 2025-01-15 19:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("facilities", "0005_auto_20250115_1918"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="facilityproduct",
            name="id",
        ),
        migrations.AlterField(
            model_name="facilityproduct",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
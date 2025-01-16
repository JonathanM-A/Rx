# Generated by Django 5.1.3 on 2024-12-20 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0011_client_last_login_alter_client_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('token', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
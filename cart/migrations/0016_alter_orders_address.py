# Generated by Django 4.2.5 on 2024-05-25 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_alter_orders_return_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='address',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cart.deliveyaddress'),
        ),
    ]

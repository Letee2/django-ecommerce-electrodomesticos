# Generated by Django 5.1.3 on 2024-11-20 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="descuento",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
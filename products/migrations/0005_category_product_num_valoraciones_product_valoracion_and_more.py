# Generated by Django 5.1.3 on 2024-11-15 17:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_product_stock"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="num_valoraciones",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="valoracion",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name="product",
            name="veces_comprado",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="categoria",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="products.category",
            ),
        ),
    ]

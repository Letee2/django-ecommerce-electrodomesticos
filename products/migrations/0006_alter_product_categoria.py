# Generated by Django 5.1.3 on 2024-11-27 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "products",
            "0005_category_product_num_valoraciones_product_valoracion_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="categoria",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.category",
            ),
            preserve_default=False,
        ),
    ]
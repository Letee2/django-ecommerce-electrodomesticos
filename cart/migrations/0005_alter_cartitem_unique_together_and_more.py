# Generated by Django 5.1.3 on 2024-11-26 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0004_merge_20241126_2011"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="session_key",
        ),
    ]
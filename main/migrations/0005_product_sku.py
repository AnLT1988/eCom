# Generated by Django 3.1.5 on 2021-01-15 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='SKU',
            field=models.TextField(default=None, max_length=8, unique=True),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-20 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='img_src',
            field=models.TextField(default=None),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-22 02:25

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_product_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', jsonfield.fields.JSONField(default=list)),
            ],
        ),
    ]

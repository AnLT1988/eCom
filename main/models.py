from django.db import models
from jsonfield import JSONField

# Create your models here.
class Category(models.Model):
    name = models.TextField(blank=False, default='')

    @classmethod
    def get_category(cls):
        return cls.objects.all()

    def get_link(self):
        return f"/{self.name}/"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    SKU = models.TextField(unique=True, blank=False, max_length=8, default=None)
    description = models.TextField(default='')
    img_src = models.TextField(blank=False, default=None)
    price = models.BigIntegerField(default=0)


class ShoppingCart(models.Model):
    items = JSONField(default=list)

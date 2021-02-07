from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
import uuid

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


class Item(models.Model):
    _product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    price = models.PositiveSmallIntegerField(default=0)
    list_price = models.PositiveIntegerField(default=0)

    @property
    def total_amount(self):
        return self.price * self.qty

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, product):
        if isinstance(product, Product):
            self._product = product
            self.price = product.price

    def __setattr__(self, attr_name, value):
        super().__setattr__(attr_name, value)
        if attr_name == "_product":
            self.price = value.price


class ShoppingCart(models.Model):
    items = models.ManyToManyField(Item, related_name="+")

    def add_or_update(self, product):
        for item in self.items.all():
            if product == item.product:
                item.qty += 1
                break
        else:
            new_item = Item.objects.create(product=product, qty=1)
            self.items.add(new_item)
            self.save()

        return self

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name="+")

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())


class Token(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField(default=uuid.uuid4)

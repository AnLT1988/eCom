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

    def add_or_update(self, product):
        for cart_item in self.cart_items.all():
            if product == cart_item.product:
                cart_item.quantity += 1
                break
        else:
            new_cart_item = CartItem.objects.create(product=product, cart=self)

        return self

    @property
    def total_amount(self):
        return sum(item.total for item in self.cart_items.all())


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, unique=False, default=None, blank=False)
    quantity = models.PositiveSmallIntegerField(default=1)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name="cart_items", default=None)

    @property
    def total(self):
        return self.quantity * self.product.price


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
            print("################", value.price)
            self.price = value.price

class Order(models.Model):
    items = models.ManyToManyField(Item, related_name="+")

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())

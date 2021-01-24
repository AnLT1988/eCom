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

    def create_or_update(self, product):
        for cart_item in self.cart_items.all():
            if product == cart_item.product:
                cart_item.quantity += 1
                break
        else:
            new_cart_item = CartItem.objects.create(product=product, cart=self)

        return self


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, unique=False, default=None, blank=False)
    quantity = models.PositiveSmallIntegerField(default=1)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name="cart_items", default=None)

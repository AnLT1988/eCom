from django.db import models

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

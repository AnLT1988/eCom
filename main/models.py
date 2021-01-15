from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.TextField(blank=False, default='')

    @classmethod
    def get_category(cls):
        return cls.objects.all()

    def get_link(self):
        return f"/{self.name}/"

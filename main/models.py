from django.db import models

# Create your models here.
class Category(models.Model):

    @staticmethod
    def get_category():
        return ['Food', 'Household', 'Computer']

from django.shortcuts import render
from django.http import HttpResponse
from main.models import Category, Product
from django.db import models

# Create your views here.

def home_page(request):
    categories = Category.get_category()
    return render(request, "home.html", {'categories': categories})

def display_category(request, category):
    category = Category.objects.get(name=category)
    products = category.product_set.all()

    return render(request, "category_view.html", {"products": products})

def display_product_detail(request, category, sku):
    products = Product.objects.all()
    return render(request, "product_detail_view.html", {"products": products})

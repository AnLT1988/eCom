from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.models import Category, Product, ShoppingCart
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
    product = Product.objects.get(SKU=sku)
    return render(request, "product_detail_view.html", {"product": product})


def add_to_cart(request, category, sku):
    ShoppingCart.objects.create(items=[sku])

    return redirect(f"/{category}/{sku}/")

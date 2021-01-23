from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
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
    cart = ShoppingCart.objects.first()
    if not cart:
        cart = ShoppingCart()

    cart.items.append(sku)
    cart.save()

    messages.add_message(request, messages.SUCCESS, "Add item to cart successfully")
    return redirect(f"/{category}/{sku}/")


def display_cart(request):
    cart = ShoppingCart.objects.first()

    return render(request, "cart_view.html", { "cart_items": cart })

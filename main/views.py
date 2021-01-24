from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from main.models import Category, Product, ShoppingCart
from django.db import models

CART_ID_SESSION_KEY = 'cart_id'

# Create your views here.

def home_page(request):
    if not request.session.get(CART_ID_SESSION_KEY, None):
        shopping_cart = ShoppingCart.objects.create()
        request.session[CART_ID_SESSION_KEY] = shopping_cart.id
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
    cart_id = request.session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    if created:
        # If new cart is created, store in session
        request.session[CART_ID_SESSION_KEY] = cart.id

    product = Product.objects.get(SKU=sku)

    cart.items.append(product.description)
    cart.save()

    messages.add_message(request, messages.SUCCESS, "Add item to cart successfully")
    return redirect(f"/{category}/{sku}/")


def display_cart(request):
    cart = ShoppingCart.objects.first()

    return render(request, "cart_view.html", { "cart_items": cart })

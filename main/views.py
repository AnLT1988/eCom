from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseServerError
from django.contrib import messages
from django.core.mail import send_mail
from main.models import Category, Product, ShoppingCart, Order
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

    cart = cart.add_or_update(product)

    messages.add_message(request, messages.SUCCESS, "Add item to cart successfully")
    return redirect("product_detail_page", category=category, sku=sku)


def display_cart(request):
    cart_id = request.session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    if created:
        # If new cart is created, store in session
        request.session[CART_ID_SESSION_KEY] = cart.id

    return render(request, "cart_view.html", { "cart_items": cart })

def update_cart(request):
    cart_id = request.session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    update_data = request.POST
    sku = update_data.getlist('item')
    quantity = update_data.getlist('quantity')

    data = [{'sku': x, 'quantity': y} for x, y in zip(sku, quantity)]

    for d in data:
        item = cart.items.get(_product__SKU=d['sku'])
        item.qty = d['quantity']
        item.save()

    messages.add_message(request, messages.SUCCESS, "update successfully")

    return redirect("shopping_cart")

def display_order_summary(request):
    cart_id = request.session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    if created:
        # If new cart is created, store in session
        request.session[CART_ID_SESSION_KEY] = cart.id

    return render(request, "order_summary.html", {'shopping_cart': cart})

def display_order_confirmation(request, order_id):
    return render(request, "order_confirmation.html", {'order': Order.objects.get(pk=order_id)})

def place_order(request):
    cart_id = request.session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    if created:
        # If new cart is created, store in session
        request.session[CART_ID_SESSION_KEY] = cart.id

    if len(cart.items.all()) == 0:
        return HttpResponseServerError()

    order = Order.objects.create()
    order.items.set(cart.items.all())
    order.save()

    message = "#" + str(order.id).zfill(9)
    send_mail(
        subject="Subject",
        message=message,
        from_email="noreply@ecom.com",
        recipient_list=["mail@mail.com"]
    )

    return redirect("order_confirmation", order_id=order.id)

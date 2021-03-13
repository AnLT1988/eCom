from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseServerError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from main.models import Category, Product, ShoppingCart, Order, Token
from django.db import models

CART_ID_SESSION_KEY = 'cart_id'

# Create your views here.
def get_cart_from_session(session):
    cart_id = session.get(CART_ID_SESSION_KEY, None)
    cart, created = ShoppingCart.objects.get_or_create(id=cart_id)

    if created:
        # If new cart is created, store in session
        session[CART_ID_SESSION_KEY] = cart.id

    return cart

def home_page(request):
    cart = get_cart_from_session(request.session)

    categories = Category.get_all_category()
    return render(request, "home.html", {'categories': categories})

def display_category(request, category):
    category = Category.objects.get(name=category)
    products = category.product_set.all()

    return render(request, "category_view.html", {"products": products})

def display_product_detail(request, category, sku):
    product = Product.objects.get(SKU=sku)
    return render(request, "product_detail_view.html", {"product": product})


def add_to_cart(request, category, sku):
    cart = get_cart_from_session(request.session)

    product = Product.objects.get(SKU=sku)

    cart = cart.add_or_update(product)

    messages.add_message(request, messages.SUCCESS, "Add item to cart successfully")
    return redirect("product_detail_page", category=category, sku=sku)


def display_cart(request):
    cart = get_cart_from_session(request.session)

    return render(request, "cart_view.html", { "cart_items": cart })

def update_cart(request):
    cart = get_cart_from_session(request.session)

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
    cart = get_cart_from_session(request.session)

    return render(request, "order_summary.html", {'shopping_cart': cart})

def display_order_confirmation(request, order_id):
    return render(request, "order_confirmation.html", {'order': Order.objects.get(pk=order_id)})

def login_view(request):
    if request.method == "POST":
        email, password, *kwargs = request.POST.values()
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect(reverse("home_page"))
        else:
            return redirect(reverse("login"))

    token = request.GET.get("token")
    try:
        token = Token.objects.get(token=token)
    except Token.DoesNotExist:
        pass
    else:
        user = token.email
        user.is_active = True
        user.save()
        render(request, "user_activation_successfull.html", {'email': user.username})

    return render(request, "login.html")

def logout_user(request):
    logout(request)
    return redirect("login")

def registration_view(request):
    return render(request, "registration.html")

def registration_success_view(request):
    email = request.GET['email']
    return render(request, "registration_success.html", {'email': email})

def register_new_user(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
    token = Token.objects.create(email=user)

    message = request.build_absolute_uri(reverse("login") + f"?token={token.token}")
    send_mail(
        subject="Activate user",
        message=message,
        from_email="admin@ecom.com",
        recipient_list=[user.email]
    )
    return redirect(f"{reverse('registration_success')}?email={email}")

def place_order(request):
    cart = get_cart_from_session(request.session)

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

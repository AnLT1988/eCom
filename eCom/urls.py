"""eCom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views as main_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view.home_page, name='home_page'),
    path('cart/', main_view.display_cart, name='shopping_cart'),
    path('<str:category>/', main_view.display_category, name='category_page'),
    path('<str:category>/<str:sku>/', main_view.display_product_detail, name='product_detail_page'),
    path('<str:category>/<str:sku>/addToCart', main_view.add_to_cart, name='add_to_cart'),
]

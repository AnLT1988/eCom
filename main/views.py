from django.shortcuts import render
from django.http import HttpResponse
from main.models import Category
from django.db import models

# Create your views here.

def home_page(request):
    categories = Category.get_category()
    return render(request, "home.html", {'categories': categories})

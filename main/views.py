from django.shortcuts import render
from django.http import HttpResponse
from main.models import get_category

# Create your views here.

def home_page(request):
    categories = get_category()
    return render(request, "home.html", {'categories': categories})

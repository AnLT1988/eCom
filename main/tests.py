from django.urls import resolve
from django.http import HttpRequest
from django.test import TestCase
from main.views import home_page
from main.models import Category

# Create your tests here.
class HomePageTest(TestCase):

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")


class ListModelTest(TestCase):

    def test_model_return_category(self):
        response = Category.get_category()
        self.assertNotIsInstance(response, str)
        try:
            for res in response:
                pass
        except:
            self.fail('Response should be iterable')

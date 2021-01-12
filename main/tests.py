from django.urls import resolve
from django.http import HttpRequest
from django.test import TestCase
from main.views import home_page

# Create your tests here.
class SmokeTest(TestCase):

    def test_can_resolve_for_root(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_return_html(self):
        request = HttpRequest()
        response = home_page(request)
        content = response.content.decode("utf-8")
        self.assertTrue(content.startswith("<html>"))
        self.assertIn("<title>eCom-Store</title>", content)

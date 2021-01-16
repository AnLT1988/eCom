from django.urls import resolve
from django.http import HttpRequest
from django.test import TestCase
from django.db.utils import IntegrityError
from main.views import home_page
from main.models import Category, Product

# Create your tests here.
class HomePageTest(TestCase):

    fixtures = ['category_data.json']

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_each_category_has_a_page(self):
        category = Category.objects.first()
        response = self.client.get(f"/{category.name}/")
        self.assertTemplateUsed(response, "category_view.html")


class ProductListViewTest(TestCase):

    def test_product_detail_view_use_correct_template(self):
        response = self.client.get("/Food/1234/")

        self.assertTemplateUsed(response, "product_detail_view.html")

    def test_product_detail_view_template_display_sufficient_detail(self):
        response = self.client.get("/Food/1234/")

        products = Product.objects.all()

        self.assertGreater(len(products), 0, "There is no product to test, setup some")

        for product in products:
            self.assertContains(response, product.discription)


class CategoryModelTest(TestCase):

    def test_model_return_category(self):
        response = Category.get_category()
        self.assertNotIsInstance(response, str)
        try:
            for res in response:
                pass
        except:
            self.fail('Response should be iterable')

    def test_can_create_new_category(self):
        category = Category()
        category.name = 'New category'
        category.save()

        self.assertIn(category, Category.objects.all())


class ProductModelTest(TestCase):

    fixtures = ['category_data.json']

    def test_can_create_new_product(self):
        category = Category.objects.first()
        product = Product(category=category, SKU=123)
        product.save()

        self.assertIn(product, Product.objects.all())

    def test_product_require_category(self):
        product = Product()
        product.SKU = '123'
        self.assertRaises(IntegrityError, product.save)

    def test_product_require_sku(self):
        product = Product()
        category = Category.objects.first()
        product.category = category

        self.assertRaises(IntegrityError, product.save)

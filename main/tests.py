from django.urls import resolve, reverse
from django.http import HttpRequest
from django.test import TestCase
from django.db.utils import IntegrityError
from main.views import home_page
from main.models import Category, Product, ShoppingCart

# Create your tests here.
class HomePageTest(TestCase):

    fixtures = ['category_data.json']

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")


class CategoryViewTest(TestCase):

    fixtures = ['category_data.json']

    def test_each_category_has_a_page(self):
        category = Category.objects.first()
        response = self.client.get(f"/{category.name}/")
        self.assertTemplateUsed(response, "category_view.html")

    def test_category_view_template_display_sufficient_detail(self):
        category = Category.objects.first()
        products = category.product_set.all()

        response = self.client.get(f"/{category.name}/")
        # self.assertContains(response, "price")

        for product in products:
            self.assertContains(response, product.description)
            self.assertContains(response, product.SKU)


class ProductDetailViewTest(TestCase):

    fixtures = ['category_data.json']

    def test_product_detail_view_use_correct_template(self):
        response = self.client.get("/Food/1234/")

        self.assertTemplateUsed(response, "product_detail_view.html")

    def test_product_detail_view_template_display_sufficient_detail(self):
        response = self.client.get("/Food/1234/")

        product = Product.objects.get(SKU="1234")

        self.assertContains(response, product.description)
        self.assertContains(response, 'description')  # Test if there a field name description

        another_product = Product.objects.get(SKU="1235")
        self.assertNotContains(response, another_product.description)

    def test_product_detail_view_has_link_to_cart(self):
        response = self.client.get("/Food/1234/")

        self.assertContains(response, reverse("shopping_cart"))

    def test_product_detail_view_has_an_image(self):
        response = self.client.get("/Food/1234/")
        product = response.context['product']

        self.assertTrue(hasattr(product, "img_src"))

    def test_redirect_after_post_to_add_to_cart(self):
        response = self.client.post("/Food/1234/addToCart")

        self.assertRedirects(response, "/Food/1234/")

    def test_post_update_the_cart_first_item(self):
        sku = 1234
        response = self.client.post(f"/Food/{sku}/addToCart")
        cart = ShoppingCart.objects.first()
        item = Product.objects.get(SKU=1234)

        self.assertIn(item.description, cart.items)

    def test_post_update_the_cart_second_item(self):
        sku = 1234
        response = self.client.post(f"/Food/{sku}/addToCart")
        cart = ShoppingCart.objects.first()
        item = Product.objects.get(SKU=sku)

        self.assertIn(item.description, cart.items)

        sku_2 = 1235
        response = self.client.post(f"/Food/{sku_2}/addToCart")
        cart = ShoppingCart.objects.first()
        item_2 = Product.objects.get(SKU=sku_2)

        self.assertIn(item.description, cart.items)
        self.assertIn(item_2.description, cart.items)


class CartViewTest(TestCase):

    fixtures = ['category_data.json']

    def test_cart_view_render_correct_template(self):
        response = self.client.get("/cart/")

        self.assertTemplateUsed(response, "cart_view.html")

    def test_cart_view_function_return_required_fields(self):
        response = self.client.get("/cart/")

        context = response.context

        cart_items = context['cart_items']

        self.assertIsInstance(cart_items.items, list)


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
        product = Product(category=category, SKU=123, img_src="abc")
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

    def test_product_has_an_image_source(self):
        product = Product()
        category = Category.objects.first()
        product.category = category
        product.SKU = 123

        self.assertRaises(IntegrityError, product.save)

    def test_product_has_a_price(self):
        product = Product()
        category = Category.objects.first()
        product.category = category
        product.SKU = 123
        product.img_src = ""

        product.save()

        self.assertTrue(hasattr(product, "price"))

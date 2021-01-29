from django.urls import resolve, reverse
from django.http import HttpRequest
from django.test import TestCase
from django.db.utils import IntegrityError
from main.views import home_page, CART_ID_SESSION_KEY
from main.models import Category, Product, ShoppingCart, CartItem
from unittest import skip

# Create your tests here.
class HomePageTest(TestCase):

    fixtures = ['category_data.json']

    def get_session_cart_id(self, response):
        session = response.client.session

        return session[CART_ID_SESSION_KEY]

    def send_request_and_get_cart_id(self):
        response = self.client.get("/")

        return self.get_session_cart_id(response)

    def test_home_page_uses_correct_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_create_a_new_cart_for_new_session(self):
        first_cart = self.send_request_and_get_cart_id()
        # Clear the current session to simulate a fresh session
        session = self.client.session
        session.flush()
        session.save()
        # Get cart id for second request
        second_cart = self.send_request_and_get_cart_id()

        self.assertNotEqual(first_cart, second_cart)

    def test_same_session_has_only_one_cart(self):
        first_cart = self.send_request_and_get_cart_id()
        second_cart = self.send_request_and_get_cart_id()

        self.assertEqual(first_cart, second_cart)


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
        cart_id = response.client.session[CART_ID_SESSION_KEY]
        cart = ShoppingCart.objects.get(id=cart_id)
        item = Product.objects.get(SKU=1234)

        self.assertIn(item, [i.product for i in cart.cart_items.all()])

    def test_post_update_the_cart_second_item(self):
        sku = 1234
        response = self.client.post(f"/Food/{sku}/addToCart")
        cart_id = response.client.session[CART_ID_SESSION_KEY]
        cart = ShoppingCart.objects.get(id=cart_id)
        item = Product.objects.get(SKU=sku)

        self.assertIn(item, [i.product for i in cart.cart_items.all()])

        sku_2 = 1235
        response = self.client.post(f"/Food/{sku_2}/addToCart")
        cart.refresh_from_db()
        item_2 = Product.objects.get(SKU=sku_2)

        cart_items = [i.product for i in cart.cart_items.all()]

        self.assertIn(item, cart_items)
        self.assertIn(item_2, cart_items)


class ShoppingCartViewTest(TestCase):

    fixtures = ['category_data.json']

    def get_session_cart_id(self, response):
        session = response.client.session

        return session[CART_ID_SESSION_KEY]

    def test_cart_view_render_correct_template(self):
        response = self.client.get("/cart/")

        self.assertTemplateUsed(response, "cart_view.html")

    def test_cart_view_shows_correct_item_being_added(self):
        sku = 1234
        self.client.post(f"/Food/{sku}/addToCart")
        item = Product.objects.get(SKU=sku)

        response = self.client.get("/cart/")
        cart_items = response.context['cart_items']

        self.assertSetEqual(set([item]), set([cart_item.product for cart_item in cart_items.cart_items.all()]))

        sku_2 = 1235
        response = self.client.post(f"/Food/{sku_2}/addToCart")
        item_2 = Product.objects.get(SKU=sku_2)
        response = self.client.get("/cart/")
        cart_items = response.context['cart_items']

        self.assertSetEqual(set([item, item_2]), set([cart_item.product for cart_item in cart_items.cart_items.all()]))

    def test_can_update_quantity_of_the_cart_item(self):
        sku = '1234'
        new_quantity = 2
        self.client.post(f"/Food/{sku}/addToCart")
        item = Product.objects.get(SKU=sku)

        response = self.client.post("/cart/update", { 'item': sku, 'quantity': new_quantity })
        cart_id = self.get_session_cart_id(response)
        shopping_cart = ShoppingCart.objects.get(id=cart_id)

        found = False
        for item in shopping_cart.cart_items.all():
            if item.product.SKU == sku:
                found = True
                self.assertEqual(new_quantity, item.quantity)

        if not found:
            self.fail("Cannot find the added product")


class OrderSummaryViewTest(TestCase):

    fixtures = ['category_data.json']

    def test_order_summary_use_correct_template(self):
        response = self.client.get(reverse("order_summary"))

        self.assertTemplateUsed(response, "order_summary.html")

    def test_order_summary_has_required_fields(self):
        sku = '1234'
        new_quantity = 2
        self.client.post(f"/Food/{sku}/addToCart")
        item = Product.objects.get(SKU=sku)

        response = self.client.get(reverse("order_summary"))

        context = response.context

        shopping_cart = context['shopping_cart']
        cart_items = shopping_cart.cart_items.all()
        self.assertGreaterEqual(len(cart_items), 1)
        for item in cart_items:
            item.quantity
            self.assertIsInstance(item.product, Product)

    def test_order_summary_has_link_to_purchase(self):
        response = self.client.get(reverse("order_summary"))

        link_to_purchase = reverse("place_order")
        self.assertContains(response, link_to_purchase)

    def test_can_place_order(self):
        response = self.client.post(reverse("place_order"))

        self.assertRedirects(response, reverse("order_confirmation"))


class OrderConfirmationViewTest(TestCase):

    def test_order_confirmation_test_use_correct_template(self):
        response = self.client.get(reverse("order_confirmation"))

        self.assertTemplateUsed(response, "order_confirmation.html")


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


class ShoppingCartModelTest(TestCase):

    fixtures = ["category_data.json"]

    def test_cart_items_have_all_product_detail(self):
        category_spec = {
            'id': '99999',
            'name': 'Test category',
        }
        category = Category.objects.create(**category_spec)

        product_spec = {
            "description": "This is a test product",
            "price": 10000,
            "img_src": "img_src",
            "SKU": "T1",
            "category": category
        }

        product = Product.objects.create(**product_spec)

        cart = ShoppingCart.objects.create()
        cart = cart.add_or_update(product)

        cart_items = cart.cart_items.all()
        self.assertTrue(all(hasattr(cart_item, "product") and hasattr(cart_item, "quantity"))
                for cart_item in cart_items)

        products = [cart_item.product for cart_item in cart_items]
        self.assertIn(product, products)

    def test_shopping_cart_has_total(self):
        category_spec = {
            'id': '99999',
            'name': 'Test category',
        }
        category = Category.objects.create(**category_spec)

        product_1_price = 10000
        product_2_price = 5000
        product_spec = {
            "description": "This is a test product",
            "price": product_1_price,
            "img_src": "img_src",
            "SKU": "T1",
            "category": category
        }

        product_spec_2 = {
            "description": "This is a test product",
            "price": product_2_price,
            "img_src": "img_src",
            "SKU": "T2",
            "category": category
        }

        product = Product.objects.create(**product_spec)
        product_2 = Product.objects.create(**product_spec_2)
        cart = ShoppingCart.objects.create()
        cart = cart.add_or_update(product)
        cart = cart.add_or_update(product_2)
        cart.save()

        expected_cart_total = product_1_price*1 + product_2_price*1

        self.assertEqual(expected_cart_total, cart.total_amount)


class CartItemModelTest(TestCase):

    fixtures = ["category_data.json"]

    def test_can_create_cart_item(self):
        category_spec = {
            'id': '99999',
            'name': 'Test category',
        }
        category = Category.objects.create(**category_spec)

        product_spec = {
            "description": "This is a test product",
            "price": 10000,
            "img_src": "img_src",
            "SKU": "T1",
            "category": category
        }

        cart_spec = {
        }

        product = Product.objects.create(**product_spec)
        cart = ShoppingCart.objects.create(**cart_spec)

        cart_item = CartItem()
        cart_item.product = product
        cart_item.cart = cart
        cart_item.save()

        saved_cart_item = CartItem.objects.last()
        self.assertEqual(cart_item, saved_cart_item)
        self.assertTrue(cart_item.product.description, product.description)
        self.assertEqual(cart_item.quantity, 1)

    def test_cart_items_can_calculate_total(self):
        cart_item = CartItem.objects.get(pk=1)

        price = cart_item.product.price
        quantity = cart_item.quantity
        expected_total = price * quantity

        self.assertEqual(expected_total, cart_item.total)

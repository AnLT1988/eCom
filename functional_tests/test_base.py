from django.test import LiveServerTestCase
from django.core import mail
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import unittest


# Look for 0 or 0.000 or \d\d.000. End with 3 character for currency, e.g. vnd usd
PRICE_REGEX = r"(\d{1,3}([\.|,]\d{3})*[\.|,]000|0)\s*\w{3}"
XPATH_CATEGORY_LIST = "//*[contains(@id, 'product_category')]"
XPATH_ITEM_CONTAINER = "//*[contains(@id, 'item_container')]"
XPATH_PRODUCT_IMAGE = "//a[@href]//img[@src]"
XPATH_SHOPPING_CART_UPDATE_BUTTON = "//button[contains(@id, 'update')]"
XPATH_SHOPPING_CART_ORDER_BUTTON = "//button[contains(@id, 'order')]"
XPATH_ORDER_SUMMARY_PURCHASE_BUTTON = "//button[contains(@id, 'purchase')]"


class NewVisitorTest(StaticLiveServerTestCase):

    fixtures = ['category_data.json']

    def setUp(self):
        self.firefox_options = Options()
        self.firefox_options.add_argument("--headless")
        self.browser = webdriver.Firefox(options=self.firefox_options)
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()

    def find_add_to_cart_button(self):
        return self.browser.find_element_by_xpath("//button[contains(text(), 'buy') or contains(text(), 'Buy') or contains(text(), 'Add to cart')]")

    def find_link_to_shopping_cart(self):
        return self.browser.find_element_by_link_text("Shopping cart")

    def navigate_to_shopping_cart(self):
        cart_link = self.find_link_to_shopping_cart()
        cart_link.click()

    def verify_shopping_cart_quantity_button(self, item):
        quantity_element = item.find_element_by_xpath('//*[contains(@id, "quantity")]')
        inc_button = item.find_element_by_xpath('//input[contains(@id, "increase")]')
        desc_button = item.find_element_by_xpath('//input[contains(@id, "decrease")]')

        current_quantity = int(quantity_element.get_attribute("value"))
        inc_button.click()
        new_quantity = item.find_element_by_xpath('//*[contains(@id, "quantity")]').get_attribute("value")

        self.assertEqual(current_quantity + 1, int(new_quantity))

    def verify_order_summary_shows_sufficient_item(self):
        items_in_table = self.get_table_rows("order_summary_table")

        # Exactly 2 items that were added
        self.assertEqual(len(items_in_table), 2)

        for item in items_in_table:
            if len(item.find_elements_by_xpath(".//th")) > 0:
                continue
            # with quantity of each item
            quantity_element_found = item.find_element_by_xpath('.//input[@type="text" and contains(@id, "quantity")]')

            # price of each unit
            price_element_found = item.find_element_by_xpath('.//input[@type="text" and contains(@id, "price")]')

            # and total amount for each items
            total_amount_element_found = item.find_element_by_xpath('.//input[@type="text" and contains(@id, "total")]')

        # as well as the total amount she has to pay
        total_order_amount_element_found = self.browser.find_element_by_xpath('//input[@type="text" and contains(@id, "totalAmount")]')

    def get_items_data_from_table_by_id(self, table_id):
        cart_items = self.get_table_rows(table_id=table_id)
        item_data = []
        for item in cart_items:
            if len(item.find_elements_by_xpath(".//th")) > 0:
                continue
            description_element = item.find_element_by_xpath(f'.//input[contains(@id, "description")]')
            quantity_element = item.find_element_by_xpath(f'.//input[contains(@id, "quantity")]')
            temp_dict = {
                "description": description_element.get_attribute("value"),
                "quantity": quantity_element.get_attribute("value")
            }
            item_data.append(temp_dict)

        return item_data

    def verify_data_present_in_order_or_cart_table(self, data, table_id):
        if isinstance(data, str):
            data = [data]

        table_data = self.get_items_data_from_table_by_id(table_id)
        for d in data:
            self.assertTrue(any("a second canned food" in item['description'] for item in table_data))


    def get_table_rows(self, table_id):
        table = self.browser.find_element_by_id(table_id)
        item_rows = table.find_elements_by_tag_name("tr")

        return item_rows

    def test_shoper_can_place_an_order(self):
        # Selenie knows about out new eCommerce site
        # so she visits the site
        self.browser.get(self.live_server_url)

        self.assertIn("eCom-Store", self.browser.title)
        # Upon getting to the site, Selenie could see some a list of product category
        # that she could click on
        categories = self.browser.find_element_by_xpath(XPATH_CATEGORY_LIST)
        items = categories.find_elements_by_tag_name("li")
        categories = [item.text.lower() for item in items]
        expected_categories = ['Food', 'Household', 'Computer']
        for expected in expected_categories:
            self.assertIn(expected.lower(), categories)
            found = self.browser.find_element_by_link_text(expected)
            self.assertTrue(found, "Cannot find the link to {}".format(expected))

        # She clicks on "Food"
        self.browser.find_element_by_link_text("Food").click()

        product_list_url = self.browser.current_url
        self.assertRegex(product_list_url, '/Food/')

        # The webpage loads a new page which show a list of food she could choose from
        items = self.browser.find_elements_by_xpath(XPATH_ITEM_CONTAINER)

        self.assertGreaterEqual(len(items), 2, "Failed to find [@id='item_container']. Was looking for list of product")
        for item in items:
            # Each food shows a clickable image
            self.assertTrue(item.find_elements_by_xpath(XPATH_PRODUCT_IMAGE), "Cannot find product image")

            # name of the food
            self.assertIn("food", item.get_attribute("innerHTML"))

            # and its price
            self.assertRegex(item.get_attribute("innerHTML"), PRICE_REGEX)

        # Selenie click on a food
        self.browser.find_element_by_xpath(XPATH_PRODUCT_IMAGE).click()

        # She was brought to the page where all details of the food could be found
        product_detail_url = self.browser.current_url
        self.assertRegex(product_detail_url, "/Food/(\d*)/")

        item_container = self.browser.find_element_by_xpath(XPATH_ITEM_CONTAINER)

        # The page show an image of the product
        try:
            self.browser.find_element_by_xpath("//img[@src]")
        except NoSuchElementException as e:
            self.fail("There's no product image could be found")


        # There's also name of the product together with description
        self.assertIn("food", item_container.get_attribute("innerHTML"))

        # and price
        self.assertRegex(item_container.get_attribute("innerHTML"), PRICE_REGEX)

        # Selenie also sees a button to buy the food with the text "Buy now"
        add_to_cart_button = self.find_add_to_cart_button()

        # Intrigued, Selenie clicks the button
        add_to_cart_button.click()

        # She then was prompted that her items has been added to the shopping cart
        # try:
            # WebDriverWait(self.browser, 3).until(EC.alert_is_present(), "Waiting for add to cart")
        # except TimeoutException as e:
            # self.fail("No alert was displayed")

        message_box = self.browser.find_element_by_id("message_box")
        self.assertIn("Add item to cart successfully", message_box.get_attribute("innerHTML"))


        # On the top of the page, she finds a link to get her to the shopping cart
        # Openning the shopping cart, Selenie is relieved to see the food she bought was there
        self.navigate_to_shopping_cart()
        shopping_cart_data = self.get_items_data_from_table_by_id("cart_item_table")

        self.assertTrue(any("a canned food" in item['description'] for item in shopping_cart_data))

        # However, just a piece of food is not enough for the dinner
        # Selenie decide to go back to the store to buy more items
        # This time, she select another food
        self.browser.get(product_list_url)
        second_product = self.browser.find_elements_by_xpath(XPATH_PRODUCT_IMAGE)[1]
        second_product.click()

        add_to_cart_button = self.find_add_to_cart_button()

        # Intrigued, Selenie clicks the button
        add_to_cart_button.click()

        # Openning the shopping cart, Selenie is relieved to see the food she bought was there
        self.navigate_to_shopping_cart()
        items_in_table = self.get_table_rows("cart_item_table")

        # Exactly 2 items that were added
        self.assertEqual(len(items_in_table), 2)

        expected_data = ["a canned food", "a second canned food"]
        self.verify_data_present_in_order_or_cart_table(expected_data, "cart_item_table")

        # Selenie turn off the browser, trying to open the browser again as another person
        self.browser.quit()

        self.browser = webdriver.Firefox(options=self.firefox_options)
        self.browser.get(self.live_server_url)

        # Openning the shopping cart, it's empty as expected.
        self.navigate_to_shopping_cart()
        items_in_table = self.get_table_rows("cart_item_table")

        self.assertEqual(len(items_in_table), 0)

        # Selenie then add another product
        self.browser.get(product_list_url)
        second_product = self.browser.find_elements_by_xpath(XPATH_PRODUCT_IMAGE)[1]

        second_product.click()

        add_to_cart_button = self.find_add_to_cart_button()

        # Intrigued, Selenie clicks the button
        add_to_cart_button.click()

        # Selenie goto the shopping cart to adjust the quantity
        self.navigate_to_shopping_cart()
        item_in_cart_table = self.browser.find_element_by_id("cart_item_table")
        items_in_table = item_in_cart_table.find_elements_by_tag_name("tr")

        # She can find the number of item showing, and a pair of button to increase and decrease
        for item in items_in_table:
            # clicking on increase, the quantity increase by one.
            self.verify_shopping_cart_quantity_button(item)

        # after increasing of the quantity, she finds that the update button was enabled
        update_button = self.browser.find_element_by_xpath(XPATH_SHOPPING_CART_UPDATE_BUTTON)

        self.assertTrue(update_button.is_enabled())

        # she clicks the button, a message shows that her cart is updated successfully
        update_button.click()
        expected_message = "update successfully"
        message_box = self.browser.find_element_by_id("message_box")
        self.assertIn(expected_message, self.browser.page_source)

        item_in_cart_table = self.browser.find_element_by_id("cart_item_table")
        items_in_table = item_in_cart_table.find_elements_by_tag_name("tr")

        item_data = self.get_items_data_from_table_by_id("cart_item_table")
        # doesn't believe, she navigate to homepage then comeback to see if her items is actually updated
        self.browser.get(self.live_server_url)
        self.navigate_to_shopping_cart()

        # when she opens the shopping cart again, the quantity of the item was indeed updated.
        item_in_cart_table = self.browser.find_element_by_id("cart_item_table")
        items_in_table = item_in_cart_table.find_elements_by_tag_name("tr")
        current_item_data = self.get_items_data_from_table_by_id("cart_item_table")

        self.assertListEqual(item_data, current_item_data)

        # After adding the food to shopping cart, Selenie want to checkout
        # by reviewing her shopping cart, she finds a button namely Order
        # clicking the Order button
        order_button = self.browser.find_element_by_xpath(XPATH_SHOPPING_CART_ORDER_BUTTON)
        order_button.click()

        # She was show the summary of her items
        self.verify_order_summary_shows_sufficient_item()

        # including all items she has selected

        self.verify_data_present_in_order_or_cart_table("a second canned food", "order_summary_table")

        # content, she pressed "Purchase"
        purchase_button = self.browser.find_element_by_xpath(XPATH_ORDER_SUMMARY_PURCHASE_BUTTON)
        purchase_button.click()

        # A congratulation message was showed and her Order Id was printed on the screen
        self.assertRegexpMatches(self.browser.page_source, r"your order is successfully created #\d{9}")
        email = mail.outbox[0]
        TEST_EMAIL = "mail@mail.com"
        self.assertIn(TEST_EMAIL, email.to)
        self.assertRegex(email.body, r".*#\d{9}")

        self.fail("Finish the functional test")


if __name__ == "__main__":
    unittest.main(warnings="ignore")

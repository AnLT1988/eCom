from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import unittest


class NewVisitorTest(StaticLiveServerTestCase):

    PRICE_REGEX = r"(\d{1,3}([\.|,]\d{3})*[\.|,]000|0)\s*\w{3}"

    fixtures = ['category_data.json']

    def setUp(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        self.browser = webdriver.Firefox(options=firefox_options)
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()

    def test_shoper_can_place_an_order(self):
        # Selenie knows about out new eCommerce site
        # so she visits the site
        self.browser.get(self.live_server_url)

        self.assertIn("eCom-Store", self.browser.title)
        # Upon getting to the site, Selenie could see some a list of product category
        # that she could click on
        categories = self.browser.find_element_by_id("product_category")
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
        items = self.browser.find_elements_by_xpath('//*/div[contains(@id, "item_container")]')

        self.assertGreaterEqual(len(items), 2, "Failed to find [@id='item_container']. Was looking for list of product")
        for item in items:
            # Each food shows a clickable image
            self.assertTrue(item.find_elements_by_xpath("a[@href]//img[@src]"), "Cannot find product image")

            # name of the food
            self.assertIn("food", item.get_attribute("innerHTML"))

            # and its price
            self.assertRegex(item.get_attribute("innerHTML"), self.PRICE_REGEX)

        # Selenie click on a food
        self.browser.find_element_by_xpath("//*/a[@href]//img").click()

        # She was brought to the page where all details of the food could be found
        product_detail_url = self.browser.current_url
        self.assertRegex(product_detail_url, "/Food/(\d*)/")

        item_container = self.browser.find_element_by_xpath('//*[contains(@id, "item_container")]')

        # The page show an image of the product
        try:
            self.browser.find_element_by_xpath("//img[@src]")
        except NoSuchElementException as e:
            self.fail("There's no product image could be found")


        # There's also name of the product together with description
        self.assertIn("food", item_container.get_attribute("innerHTML"))

        # and price
        self.assertRegex(item_container.get_attribute("innerHTML"), self.PRICE_REGEX)

        # Selenie also sees a button to buy the food with the text "Buy now"
        add_to_cart_button = self.browser.find_element_by_xpath("//button[contains(text(), 'buy') or contains(text(), 'Buy') or contains(text(), 'Add to cart')]")

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
        cart_link = self.browser.find_element_by_link_text("Shopping cart")

        # Openning the shopping cart, Selenie is relieved to see the food she bought was there
        cart_link.click()
        item_in_cart_table = self.browser.find_element_by_id("cart_item_table")

        self.assertInHTML("Food", item_in_cart_table.get_attribute("innerHTML"))

        # However, just a piece of food is not enough for the dinner
        # Selenie decide to go back to the store to buy more items
        # This time, she select another food
        self.browser.get(product_list_url)
        self.browser.find_elements_by_xpath("//*/a[@href]//img")[1].click()

        cart_link = self.browser.find_element_by_link_text("Shopping cart")

        # Openning the shopping cart, Selenie is relieved to see the food she bought was there
        cart_link.click()
        item_in_cart_table = self.browser.find_element_by_id("cart_item_table")

        self.assertInHTML("a canned food", item_in_cart_table.get_attribute("innerHTML"))
        self.assertInHTML("a second canned food", item_in_cart_table.get_attribute("innerHTML"))

        # After adding the food to shopping cart, Selenie want to checkout
        # by reviewing her shopping cart, she finds a button namely Order
        # clicking the Order button

        # She was show the summary of her items
        # including all items she has selected

        # with quantity of each item

        # price of each unit

        # and total amount for each items

        # as well as the total amount she has to pay

        # content, she pressed "Purchase"

        # A congratulation message was showed and her Order Id was printed on the screen
        self.fail("Finish the functional test")


if __name__ == "__main__":
    unittest.main(warnings="ignore")

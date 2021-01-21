from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import unittest


class NewVisitorTest(StaticLiveServerTestCase):

    fixtures = ['category_data.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)

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

        url = self.browser.current_url
        self.assertRegex(url, '/Food/')

        # The webpage loads a new page which show a list of food she could choose from
        items = self.browser.find_elements_by_xpath('//*/div[contains(@id, "item_container")]')

        self.assertGreaterEqual(len(items), 2, "Failed to find [@id='item_container']. Was looking for list of product")
        for item in items:
            # Each food shows a clickable image
            self.assertTrue(item.find_elements_by_xpath("a[@href]//img[@src]"), "Cannot find product image")

            # name of the food
            self.assertIn("food", item.get_attribute("innerHTML"))

            # and its price
            self.assertRegex(item.get_attribute("innerHTML"), r"(\d{1,3}([\.|,]\d{3})*[\.|,]000|0)\s*\w{3}")

        # Selenie click on a food
        self.browser.find_element_by_xpath("//*/a[@href]//img").click()

        # She was brought to the page where all details of the food could be found
        url = self.browser.current_url
        self.assertRegex(url, "/Food/(\d*)/")

        item_container = self.browser.find_element_by_xpath('//*[contains(@id, "item_container")]')

        # The page show an image of the product
        try:
            self.browser.find_element_by_xpath("//img[@src]")
        except NoSuchElementException as e:
            self.fail("There's no product image could be found")


        # There's also name of the product together with description
        self.assertIn("food", item_container.get_attribute("innerHTML"))

        # and price
        self.assertRegex(item_container.get_attribute("innerHTML"), r"(\d{1,3}([\.|,]\d{3})*[\.|,]000|0)\s*\w{3}")

        # Selenie also sees a button to buy the food with the text "Buy now"

        # Intrigued, Selenie clicks the button

        # She then was prompted that her items has been added to the shopping cart

        # On the top of the page, she finds a link to get her to the shopping cart

        # Openning the shopping cart, Selenie is relieved to see the food she bought was there

        # However, just a piece of food is not enough for the dinner
        # Selenie decide to go back to the store to buy more items
        # This time, she select another food

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

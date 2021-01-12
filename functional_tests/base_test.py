from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_shoper_can_place_an_order(self):
        # Selenie knows about out new eCommerce site
        # so she visits the site
        self.browser.get("http://localhost:8000")

        self.assertIn("eCom-Store", self.browser.title)
        # Upon getting to the site, Selenie could see some a list of product category
        # that she could click on

        # She clicks on "Food"

        # The webpage loads a new page which show a list of food she could choose from
        # Each food shows an image

        # name of the food

        # and its price

        # Selenie click on a food

        # She was brought to the page where all details of the food could be found

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


if __name__ == "__main__":
    unittest.main(warnings="ignore")

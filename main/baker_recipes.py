from model_bakery.recipe import Recipe, foreign_key
from main.models import Product, Item, Order

tc_01_product = Recipe(Product, _fill_optional=True)
tc_01_item = Recipe(
        Item,
        _product=foreign_key('tc_01_product'),
        qty=2,
        price=10000)
tc_01_expected_result = 20000

tc_02_order = Recipe(Order, _fill_optional=True)

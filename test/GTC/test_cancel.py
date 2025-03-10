import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, OrderStatus, todecimal
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)

class TestOrdersGTC(unittest.TestCase):
    def setUp(self): 
        logging.basicConfig(level=logging.ERROR)
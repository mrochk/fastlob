import unittest
from hypothesis import given, strategies as st

from fastlob import OrderSide
from fastlob.enums import OrderStatus
from fastlob.side import AskSide, BidSide
from fastlob.order import AskOrder, BidOrder, OrderParams
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

class TestSide(unittest.TestCase):
    def setUp(self): pass

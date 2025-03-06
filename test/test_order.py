import unittest
from decimal import Decimal
from hypothesis import given
import hypothesis.strategies as st
import time

from fastlob import OrderParams
from fastlob.consts import MAX_VALUE, MIN_VALUE
from fastlob.enums import OrderSide, OrderType, OrderStatus
from fastlob.utils import todecimal
from fastlob.order import Order, BidOrder, AskOrder

valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_quantity = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_fill = st.decimals(min_value=MIN_VALUE*2, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_order_side = st.sampled_from(OrderSide)
valid_order_type = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry = st.one_of(st.none(), st.floats(min_value=0, allow_nan=False, allow_infinity=False))

class TestOrder(unittest.TestCase):
    def setUp(self): pass
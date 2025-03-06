import unittest
from decimal import Decimal
from hypothesis import given, strategies as st
import secrets

from fastlob.limit import Limit
from fastlob.enums import OrderSide, OrderStatus
from fastlob.order import OrderParams, BidOrder, AskOrder
from fastlob.consts import MIN_VALUE, MAX_VALUE
from fastlob.utils import todecimal

valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_side = st.sampled_from(OrderSide)
valid_order_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
random_uuid = st.sampled_from([secrets.token_urlsafe(8) for _ in range(1000)])

class TestLimit(unittest.TestCase):
    def setUp(self): pass
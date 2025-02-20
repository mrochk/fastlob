import unittest
from hypothesis import given, strategies as st
import random

from pylob import OrderBook, OrderSide, OrderParams, OrderType
from pylob.orderbook.result import LimitResult
from pylob.enums import OrderStatus
from pylob.consts import MIN_VALUE, MAX_VALUE

n_orders_big = st.integers(min_value=1, max_value=1e4)
n_orders_small = st.integers(min_value=1, max_value=1e3)

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

'''
There is no such thing as a FOK limit order, it should never succeed.
'''

class TestLimitOrders(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestLimitOrders')

    @given(valid_side, valid_price, valid_qty)
    def test_one_fail(self, side, price, qty):
        '''If the book is empty, then any order is a limit order, and thus if set as FOK it should fail.'''
        self.ob.reset()

        op = OrderParams(side, price, qty, otype=OrderType.FOK)
        result : LimitResult = self.ob.process_one(op)

        self.assertTrue(isinstance(result, LimitResult))
        self.assertFalse(result.success())
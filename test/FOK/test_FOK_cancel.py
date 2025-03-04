import unittest
from hypothesis import given, strategies as st

from fastlob import OrderBook, OrderSide, OrderParams, OrderType
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE-10, allow_infinity=False, allow_nan=False)

'''
There is no such thing as cancelling a FOK order, if it is invalid, it is not processed, otherwise it is entirely filled.
'''

class TestCancel(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestCancel')

    @given(valid_side, valid_price, valid_qty)
    def test_fail_invalid(self, side, price, qty):
        self.ob.reset()

        fok = OrderParams(side, price, qty, otype=OrderType.FOK)
        
        r = self.ob(fok)
        self.assertFalse(r.success())
        
        cr = self.ob.cancel_order(r.order_id())
        self.assertFalse(cr.success())
     
    @given(valid_side, valid_price, valid_qty)
    def test_fail_valid(self, side, price, qty):
        self.ob.reset()

        limit = OrderParams(side, price, qty, otype=OrderType.GTC)
        r = self.ob(limit)
        self.assertTrue(r.success())

        fok = OrderParams(OrderSide.invert(side), price, qty, otype=OrderType.FOK)
        r = self.ob(fok)
        self.assertTrue(r.success())

        cr = self.ob.cancel_order(r.order_id())
        self.assertFalse(cr.success())
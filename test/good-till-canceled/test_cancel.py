import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, OrderStatus, todecimal
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)

class TestCancelGTC(unittest.TestCase):
    def setUp(self): 
        logging.basicConfig(level=logging.ERROR)

    @given(valid_side, valid_price, valid_price)
    def test_cancel_one_limit(self, side, price, qty):
        self.lob = Orderbook('TestCancelGTC')
        self.lob.start()

        p = OrderParams(side, price, qty, OrderType.GTC, expiry=None)

        r = self.lob(p)

        self.assertTrue(r.success())
        self.assertEqual(self.lob.n_prices(), 1)

        cr = self.lob.cancel(r.orderid())

        self.assertTrue(cr.success())
        self.assertEqual(self.lob.n_prices(), 0)

        self.lob.stop()
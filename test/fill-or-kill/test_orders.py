import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, OrderStatus, todecimal, ResultType
from fastlob.enums import ResultType
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE - MIN_VALUE, allow_nan=False, allow_infinity=False)

class TestOrdersFOK(unittest.TestCase):
    def setUp(self): 
        logging.basicConfig(level=logging.ERROR)

    @given(valid_side, valid_price, valid_qty)
    def test_place_limit(self, side, price, qty):
        # can not place a fok order

        lob = Orderbook('TestOrdersFOK')
        lob.start()

        op = OrderParams(side, price, qty, OrderType.FOK)

        r = lob(op)

        self.assertFalse(r.success())

        lob.stop()
        
    @given(valid_price, valid_qty)
    def test_place_error_qty(self, price, qty):
        # can not place a fok order

        lob = Orderbook('TestOrdersFOK')
        lob.start()

        price = 100

        op = OrderParams(OrderSide.ASK, price, qty, OrderType.GTC)
        r = lob(op)

        self.assertTrue(r.success())

        op2 = OrderParams(OrderSide.BID, price, qty + MIN_VALUE, OrderType.FOK)
        r2 = lob(op2)

        #lob.render()

        self.assertFalse(r2.success())

        lob.stop()
        
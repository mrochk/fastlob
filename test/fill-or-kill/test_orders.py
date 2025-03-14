import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, todecimal
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE - MIN_VALUE, allow_nan=False, allow_infinity=False)
valid_qty2 = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE // 1000 - MIN_VALUE, allow_nan=False, allow_infinity=False)

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
        # testing that a fok order is not placed if its quantity can not be matched, for one order sitting at one price level

        qty = todecimal(qty)

        lob = Orderbook('TestOrdersFOK')
        lob.start()

        price = 100

        op = OrderParams(OrderSide.ASK, price, qty, OrderType.GTC)
        r = lob(op)

        self.assertTrue(r.success())

        op2 = OrderParams(OrderSide.BID, price, qty + MIN_VALUE, OrderType.FOK)
        r2 = lob(op2)

        self.assertFalse(r2.success())

        op3 = OrderParams(OrderSide.BID, price, quantity=qty, otype=OrderType.FOK)
        r3 = lob(op3)
        self.assertTrue(r3.success())

        lob.stop()
        
    @given(valid_price, valid_qty2)
    def test_place_error_qty2(self, price, qty):
        # testing that a fok order is not placed if its quantity can not be matched, for many orders sitting at one price level

        qty = todecimal(qty)

        lob = Orderbook('TestOrdersFOK')
        lob.start()

        ops = [OrderParams(OrderSide.ASK, price, qty, OrderType.GTC)]*1000
        rs = lob(ops)

        op2 = OrderParams(OrderSide.BID, price, quantity=1000 * qty + MIN_VALUE, otype=OrderType.FOK)
        r2 = lob(op2)

        self.assertFalse(r2.success())

        op3 = OrderParams(OrderSide.BID, price, quantity=1000 * qty, otype=OrderType.FOK)
        r3 = lob(op3)
        self.assertTrue(r3.success())

        lob.stop()

    @given(valid_price, valid_qty2)
    def test_place_error_qty3(self, price, qty):
        # testing that a fok order is not placed if its quantity can not be matched, for many orders sitting at different price levels

        qty = todecimal(qty)

        lob = Orderbook('TestOrdersFOK')
        lob.start()

        price = 100
        
        for i in range(1000):
            op = OrderParams(OrderSide.ASK, price + i, qty, OrderType.GTC)
            r = lob(op)
            self.assertTrue(r.success())

        op2 = OrderParams(OrderSide.BID, price, quantity=qty + MIN_VALUE, otype=OrderType.FOK)
        r2 = lob(op2)
        self.assertFalse(r2.success())

        op3 = OrderParams(OrderSide.BID, price+1000, quantity=1000*qty + MIN_VALUE, otype=OrderType.FOK)
        r3 = lob(op3)
        self.assertFalse(r3.success())

        op4 = OrderParams(OrderSide.BID, price+1000, quantity=1000*qty, otype=OrderType.FOK)
        r4 = lob(op4)
        self.assertTrue(r4.success())

        lob.stop()
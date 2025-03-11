import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, OrderStatus
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

        s, q = self.lob.get_status(cr.orderid())

        self.assertEqual(s, OrderStatus.CANCELED)
        self.assertEqual(q, p.quantity)

        self.lob.stop()

    @given(valid_side, valid_price, valid_price)
    def test_cancel_one_limit_2(self, side, price, qty):
        self.lob = Orderbook('TestCancelGTC')
        self.lob.start()

        p = OrderParams(side, price, qty, OrderType.GTC, expiry=None)

        r = self.lob(p)

        self.assertTrue(r.success())
        self.assertEqual(self.lob.n_prices(), 1)

        p2 = OrderParams(side, price, qty, OrderType.GTC, expiry=None)

        r2 = self.lob(p)

        self.assertTrue(r2.success())
        self.assertEqual(self.lob.n_prices(), 1)

        cr = self.lob.cancel(r.orderid())

        self.assertTrue(cr.success())
        self.assertEqual(self.lob.n_prices(), 1)

        s, q = self.lob.get_status(cr.orderid())

        self.assertEqual(s, OrderStatus.CANCELED)
        self.assertEqual(q, p.quantity)

        cr = self.lob.cancel(r2.orderid())

        self.assertTrue(cr.success())
        self.assertEqual(self.lob.n_prices(), 0)

        s, q = self.lob.get_status(cr.orderid())

        self.assertEqual(s, OrderStatus.CANCELED)
        self.assertEqual(q, p.quantity)

        self.lob.stop()

    def test_cancel_exec(self):
        self.lob = Orderbook('TestCancelGTC')
        self.lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, expiry=None)
        p2 = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, expiry=None)

        r, r2 = self.lob([p, p2])

        self.assertTrue(r.success())
        self.assertTrue(r2.success())
        self.assertEqual(self.lob.n_prices(), 1)

        cr = self.lob.cancel(r.orderid())

        self.assertTrue(cr.success())

        p3 = OrderParams(OrderSide.BID, 100, 15, OrderType.GTC, expiry=None)

        r3 = self.lob(p3)

        self.assertTrue(r3.success())

        self.assertEqual(self.lob.n_bids(), 1)

        self.assertEqual(self.lob.get_status(r3.orderid())[1], 5)

        self.lob.stop()

    def test_cancel_after_partial_fill(self):
        lob = Orderbook('TestCancelGTC')
        lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, expiry=None)

        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_asks(), 1)

        partial = OrderParams(OrderSide.BID, 100, 5)

        r2 = lob(partial)

        self.assertTrue(r2.success())
        self.assertEqual(lob.n_asks(), 1)

        s, q = lob.get_status(r.orderid())

        self.assertEqual(s, OrderStatus.PARTIAL)
        self.assertEqual(q, 5)

        cr = lob.cancel(r.orderid())

        self.assertTrue(cr.success())
        self.assertEqual(lob.n_prices(), 0)

        lob.stop()

    def test_cancel_after_complete_fill(self):
        lob = Orderbook('TestCancelGTC')
        lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, expiry=None)

        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_asks(), 1)

        full = OrderParams(OrderSide.BID, 100, 10)

        r2 = lob(full)

        self.assertTrue(r2.success())
        self.assertEqual(lob.n_asks(), 0)

        s, q = lob.get_status(r.orderid())

        self.assertEqual(s, OrderStatus.FILLED)
        self.assertEqual(q, 0)

        cr = lob.cancel(r.orderid())

        self.assertFalse(cr.success())

        lob.stop()

    def test_cancel_after_cancel(self):
        lob = Orderbook('TestCancelGTC')
        lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, expiry=None)

        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_asks(), 1)

        cr = lob.cancel(r.orderid())

        self.assertTrue(cr.success())

        cr = lob.cancel(r.orderid())

        self.assertFalse(cr.success())

        lob.stop()
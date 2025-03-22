import unittest, logging, time
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderStatus, OrderParams, OrderSide, OrderType, todecimal
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE - MIN_VALUE, allow_nan=False, allow_infinity=False)
valid_qty2 = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE // 1000 - MIN_VALUE, allow_nan=False, allow_infinity=False)

def valid_expiry(x:int = 5): return int(time.time()) + x

class TestOrdersGTD(unittest.TestCase):
    def setUp(self): 
        logging.basicConfig(level=logging.ERROR)

    @given(valid_side, valid_price, valid_qty)
    def test_init(self, side, price, qty):
        with self.assertRaises(ValueError):
            OrderParams(side, price, qty, OrderType.GTD)

        with self.assertRaises(ValueError):
            OrderParams(side, price, qty, OrderType.GTD, expiry=time.time())

        OrderParams(side, price, qty, OrderType.GTD, expiry=valid_expiry())

    @given(valid_side, valid_price, valid_qty)
    def test_place(self, side, price, qty):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        p = OrderParams(side, price, qty, OrderType.GTD, expiry=valid_expiry(10))
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        lob.stop()

    @given(valid_side, valid_price, valid_qty)
    def test_place_then_cancel(self, side, price, qty):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        p = OrderParams(side, price, qty, OrderType.GTD, expiry=valid_expiry(10))
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        cr = lob.cancel(r.orderid())
        self.assertTrue(cr.success())

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.CANCELED)

        lob.stop()

    def test_place_fill(self):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        side = OrderSide.ASK
        price = 100
        qty = 10

        p = OrderParams(side, price, qty, OrderType.GTD, expiry=valid_expiry(2))
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        p2 = OrderParams(OrderSide.invert(side), price, qty)
        r2 = lob(p2)
        self.assertTrue(r2.success())

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.FILLED)

        time.sleep(3.11)

        # check that order is not canceled if it is filled

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.FILLED)

        lob.stop()

    def test_expiration(self):
        self.setUp()
        lob = Orderbook('TestOrdersGTD'); lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTD, expiry=valid_expiry(2))
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        time.sleep(3.11)

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.CANCELED)

        lob.stop()

    def test_market_is_not_canceled(self):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC)
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        gtd = OrderParams(OrderSide.BID, 100, 5, OrderType.GTD, expiry=valid_expiry(2))
        rgtd = lob(gtd)
        self.assertTrue(rgtd.success())

        s, _ = lob.get_status(rgtd.orderid())
        self.assertEqual(s, OrderStatus.FILLED)

        time.sleep(3.11)

        s, _ = lob.get_status(rgtd.orderid())
        self.assertEqual(s, OrderStatus.FILLED)

        lob.stop()

    def test_canceled_after_market_partial_fill(self):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        p = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC)
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        gtd = OrderParams(OrderSide.BID, 100, 15, OrderType.GTD, expiry=valid_expiry(2))
        rgtd = lob(gtd)
        self.assertTrue(rgtd.success())

        s, _ = lob.get_status(rgtd.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        time.sleep(3.11)

        s, q = lob.get_status(rgtd.orderid())
        self.assertEqual(s, OrderStatus.CANCELED)
        self.assertEqual(q, 5)

        lob.stop()

    def test_partial_fill_then_cancel(self):
        lob = Orderbook('TestOrdersGTD'); lob.start()

        side = OrderSide.ASK
        price = 100
        qty = 10

        p = OrderParams(side, price, qty, OrderType.GTD, expiry=valid_expiry(2))
        r = lob(p)

        self.assertTrue(r.success())
        self.assertEqual(lob.n_prices(), 1)
        
        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PENDING)

        p2 = OrderParams(OrderSide.invert(side), price, qty // 2)
        r2 = lob(p2)
        self.assertTrue(r2.success())

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.PARTIAL)

        time.sleep(3.11)

        s, _ = lob.get_status(r.orderid())
        self.assertEqual(s, OrderStatus.CANCELED)

        lob.stop()

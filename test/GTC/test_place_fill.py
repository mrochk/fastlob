import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook, OrderParams, OrderSide, OrderType, OrderStatus, todecimal
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)

class TestOrdersGTC(unittest.TestCase):
    def setUp(self): 
        logging.basicConfig(level=logging.ERROR)
        
    @given(valid_side, valid_price, valid_qty)
    def test_place_one(self, side, price, qty):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = OrderParams(side, price, qty, OrderType.GTC, expiry=None)
        r = self.lob(params)

        self.assertTrue(r.success())

        self.assertEqual(self.lob.n_prices(), 1)

        if side == OrderSide.ASK:
            self.assertEqual(self.lob.n_asks(), 1)
            self.assertEqual(self.lob.best_ask(), params.price)
        else:
            self.assertEqual(self.lob.n_bids(), 1)
            self.assertEqual(self.lob.best_bid(), params.price)

        s, q = self.lob.get_status(r.orderid())

        self.assertEqual(s, OrderStatus.PENDING)
        self.assertEqual(q, params.quantity)

        self.lob.stop()

    def test_place_many(self):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = list()

        N = 40_000

        for i in range(N):
            p = OrderParams(OrderSide.ASK, 50_000+i, 10, OrderType.GTC, expiry=None)
            params.append(p)

            p = OrderParams(OrderSide.BID, 50_000-1-i, 10, OrderType.GTC, expiry=None)
            params.append(p)

        results = self.lob(params)

        self.assertTrue(all([r.success() for r in results]))

        self.assertEqual(self.lob.n_asks(), N)
        self.assertEqual(self.lob.n_prices(), 2*N)

        for r in results:
            s, q = self.lob.get_status(r.orderid())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, 10)

        self.lob.stop()

    @given(valid_side, valid_price, valid_qty)
    def test_fill_one(self, side, price, qty):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = OrderParams(side, price, qty, OrderType.GTC, expiry=None)
        r = self.lob(params)

        self.assertTrue(r.success())

        self.assertEqual(self.lob.n_prices(), 1)

        matching_order = OrderParams(OrderSide.invert(side), price, qty, OrderType.GTC)

        mr = self.lob(matching_order)

        self.assertTrue(mr.success())

        s1, q1 = self.lob.get_status(r.orderid())
        s2, q2 = self.lob.get_status(mr.orderid())

        self.assertEqual(s1, OrderStatus.FILLED)
        self.assertEqual(s2, OrderStatus.FILLED)

        self.assertEqual(q1, 0)
        self.assertEqual(q2, 0)

        self.lob.stop()

    def test_fill_many(self):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = list()

        N = 40_000

        for i in range(N):
            p = OrderParams(OrderSide.ASK, 50_000+i, 10, OrderType.GTC, expiry=None)
            params.append(p)

            p = OrderParams(OrderSide.BID, 50_000-1-i, 10, OrderType.GTC, expiry=None)
            params.append(p)

        results = self.lob(params)

        self.assertTrue(all([r.success() for r in results]))

        matching_ask = OrderParams(OrderSide.BID, 90_000, 400_000, OrderType.GTC)
        mr1 = self.lob(matching_ask)

        self.assertTrue(mr1.success())
        self.assertEqual(self.lob.n_asks(), 0)

        matching_bid = OrderParams(OrderSide.ASK, 1, 400_000, OrderType.GTC)
        mr2 = self.lob(matching_bid)

        self.assertTrue(mr2.success())
        self.assertEqual(self.lob.n_bids(), 0)

        for r in results + [mr1, mr2]:
            s, _ = self.lob.get_status(r.orderid())
            self.assertEqual(s, OrderStatus.FILLED)

        self.lob.stop()

    @given(valid_side, valid_price)
    def test_partially_fill_one(self, side, price):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = OrderParams(side, price, 10, OrderType.GTC, expiry=None)
        r = self.lob(params)

        self.assertTrue(r.success())

        matching_order = OrderParams(OrderSide.invert(side), price, 5)

        mr = self.lob(matching_order)

        self.assertTrue(mr.success())

        s1, q = self.lob.get_status(r.orderid())
        s2, _ = self.lob.get_status(mr.orderid())

        self.assertEqual(s1, OrderStatus.PARTIAL)
        self.assertEqual(q, 5)
        self.assertEqual(s2, OrderStatus.FILLED)

        self.lob.stop()

    @given(valid_side, valid_price)
    def test_fill_limit(self, side, price):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = [OrderParams(side, price, 10, OrderType.GTC, expiry=None)] * 10
        results = self.lob(params)

        self.assertTrue(all([r.success() for r in results]))

        matching_order = OrderParams(OrderSide.invert(side), price, 100)

        mr = self.lob(matching_order)

        self.assertTrue(mr.success())

        self.assertEqual(self.lob.n_prices(), 0)

        self.assertEqual(self.lob.n_prices(), 0)

        for r in results + [mr]:
            s, _ = self.lob.get_status(r.orderid())
            self.assertEqual(s, OrderStatus.FILLED)

        self.lob.stop()

    @given(valid_side, valid_price)
    def test_order_placed_if_not_filled(self, side, price):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = OrderParams(side, price, 10, OrderType.GTC, expiry=None)
        result = self.lob(params)

        self.assertTrue(result.success())

        matching_order = OrderParams(OrderSide.invert(side), price, 15)
        mr = self.lob(matching_order)

        s, q = self.lob.get_status(mr.orderid())

        self.assertEqual(s, OrderStatus.PENDING)
        self.assertEqual(q, 5)

        s, q = self.lob.get_status(result.orderid())

        self.assertEqual(s, OrderStatus.FILLED)
        self.assertEqual(q, 0)

        self.lob.stop()

    @given(valid_side, valid_price)
    def test_order_placed_if_not_filled2(self, side, price):
        self.lob = Orderbook('TestGTC')
        self.lob.start()

        self.assertEqual(self.lob.n_prices(), 0)

        params = [OrderParams(side, price, 10, OrderType.GTC, expiry=None)]*10
        result = self.lob(params)

        matching_order = OrderParams(OrderSide.invert(side), price, 104.67)
        mr = self.lob(matching_order)

        s, q = self.lob.get_status(mr.orderid())

        self.assertEqual(s, OrderStatus.PENDING)
        self.assertEqual(q, todecimal(4.67))

        for r in result:

            s, q = self.lob.get_status(r.orderid())

            self.assertEqual(s, OrderStatus.FILLED)
            self.assertEqual(q, 0)

        self.lob.stop()
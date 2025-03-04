import unittest
from hypothesis import given, strategies as st, settings
import random

from fastlob import OrderBook, OrderSide, OrderParams
from fastlob.orderbook.result import LimitResult
from fastlob.enums import OrderStatus
from fastlob.consts import MIN_VALUE, MAX_VALUE

n_orders = st.integers(min_value=1, max_value=100)

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE*2, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

class TestLimitOrders(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestLimitOrders')

    @given(valid_side, valid_price, valid_qty)
    def test_one(self, side, price, qty):
        self.ob.reset()

        op = OrderParams(side, price, qty)
        result : LimitResult = self.ob(op)

        self.assertIsInstance(result, LimitResult)
        self.assertTrue(result.success())

        if side == OrderSide.BID:
            self.assertEqual(self.ob.best_bid(), op.price)
            self.assertEqual(self.ob.n_bids(), 1)
        else: 
            self.assertEqual(self.ob.best_ask(), op.price)
            self.assertEqual(self.ob.n_asks(), 1)
        
        s, q = self.ob.get_order_status(result.order_id())

        self.assertEqual(s, OrderStatus.PENDING)
        self.assertEqual(q, op.quantity)

    @given(n_orders, valid_side, valid_price)
    def test_many_same_price(self, n, side, price):
        self.ob.reset()

        ordersparams = [OrderParams(side, price, random.randint(1, int(10e9))) for _ in range(n)]

        results : list[LimitResult] = self.ob(ordersparams)

        if side == OrderSide.BID:
            self.assertEqual(self.ob.n_bids(), 1)
            self.assertEqual(self.ob.best_bid(), ordersparams[0].price)
        else: 
            self.assertEqual(self.ob.n_asks(), 1)
            self.assertEqual(self.ob.best_ask(), ordersparams[0].price)

        for i, result in enumerate(results):

            self.assertIsInstance(result, LimitResult)
            self.assertTrue(result.success())

            s, q = self.ob.get_order_status(result.order_id())

            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, ordersparams[i].quantity) 

    @given(n_orders, valid_side)
    def test_many_different_price(self, n, side):
        self.ob.reset()

        ordersparams = list()

        for _ in range(n):
            p = random.randint(1, int(10e9))
            q = random.randint(1, int(10e9))
            op = OrderParams(side, p, q)
            ordersparams.append(op)

        results = self.ob(ordersparams)

        self.assertEqual(self.ob.n_prices(), n)

        for i, result in enumerate(results):

            self.assertIsInstance(result, LimitResult)
            self.assertTrue(result.success())
            s, q = self.ob.get_order_status(result.order_id())

            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, ordersparams[i].quantity) 

    @given(n_orders, valid_price)
    def test_many_same_price_both_sides(self, n, price):
        self.ob.reset()

        ordersparams = list()

        from fastlob import todecimal

        pbid = price - todecimal('0.01')
        pask = price

        for _ in range(n):

            qbid = random.randint(1, int(10e9))
            opbid = OrderParams(OrderSide.BID, pbid, qbid)

            qask = random.randint(1, int(10e9))
            opask = OrderParams(OrderSide.ASK, pask, qask)

            ordersparams.append(opbid)
            ordersparams.append(opask)

        results : LimitResult = self.ob(ordersparams)

        self.assertEqual(self.ob.n_asks(), self.ob.n_bids())
        self.assertEqual(self.ob.n_prices(), 2)

        for i, result in enumerate(results):

            self.assertTrue(result.success())
            self.assertIsInstance(result, LimitResult)

            s, q = self.ob.get_order_status(result.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, ordersparams[i].quantity) 

            self.assertTrue(self.ob.best_bid() == ordersparams[i].price or self.ob.best_ask() == ordersparams[i].price)

    @given(n_orders)
    def test_many_different_price_both_sides(self, n):
        self.ob.reset()

        ordersparams = list()

        for _ in range(n):

            pbid = random.randint(1, int(10e6))
            qbid = random.randint(1, int(10e9))
            opbid = OrderParams(OrderSide.BID, pbid, qbid)

            pask = random.randint(int(10e7), int(10e9))
            qask = random.randint(1, int(10e9))
            opask = OrderParams(OrderSide.ASK, pask, qask)

            ordersparams.append(opbid)
            ordersparams.append(opask)

        results = self.ob(ordersparams)

        self.assertEqual(self.ob.n_asks(), self.ob.n_bids())
        self.assertEqual(self.ob.n_prices(), n+n)

        for i, result in enumerate(results):
            self.assertTrue(result.success())
            self.assertIsInstance(result, LimitResult)

            s, q = self.ob.get_order_status(result.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, ordersparams[i].quantity) 
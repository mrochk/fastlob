import unittest
from hypothesis import given, strategies as st
import random

from pylob import OrderBook, OrderSide, OrderParams
from pylob.orderbook.result import LimitResult
from pylob.enums import OrderStatus
from pylob.consts import MIN_VALUE, MAX_VALUE

n_orders_big = st.integers(min_value=1, max_value=1e4)
n_orders_small = st.integers(min_value=1, max_value=1e3)

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

class TestLimitOrders(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestLimitOrders')

    @given(valid_side, valid_price, valid_qty)
    def test_one(self, side, price, qty):
        self.setUp()

        op = OrderParams(side, price, qty)
        result : LimitResult = self.ob.process_one(op)

        self.assertIsInstance(result, LimitResult)
        self.assertTrue(result.success())

        if side == OrderSide.BID:
            self.assertEqual(self.ob.best_bid(), op.price)
            self.assertEqual(self.ob.n_bids(), 1)
        else: 
            self.assertEqual(self.ob.best_ask(), op.price)
            self.assertEqual(self.ob.n_asks(), 1)
        
        s, q = self.ob.get_order(result.order_id())

        self.assertEqual(s, OrderStatus.PENDING)
        self.assertEqual(q, op.quantity)

    @given(n_orders_big, valid_side, valid_price)
    def test_many_same_price(self, n, side, price):
        self.setUp()

        for _ in range(n):

            q = random.randint(1, int(10e9))
            op = OrderParams(side, price, q)
            result : LimitResult = self.ob.process_one(op)

            self.assertIsInstance(result, LimitResult)
            self.assertTrue(result.success())

            if side == OrderSide.BID:
                self.assertEqual(self.ob.n_bids(), 1)
                self.assertEqual(self.ob.best_bid(), op.price)
            else: 
                self.assertEqual(self.ob.n_asks(), 1)
                self.assertEqual(self.ob.best_ask(), op.price)
        
            s, q = self.ob.get_order(result.order_id())

            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, op.quantity) 

    @given(n_orders_small, valid_side)
    def test_many_different_price(self, n, side):
        self.setUp()

        for i in range(1, n+1):

            p = random.randint(1, int(10e9))
            q = random.randint(1, int(10e9))
            op = OrderParams(side, p, q)

            result : LimitResult = self.ob.process_one(op)

            self.assertIsInstance(result, LimitResult)
            self.assertTrue(result.success())

            self.assertEqual(self.ob.n_prices(), i)
        
            s, q = self.ob.get_order(result.order_id())

            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, op.quantity) 

    @given(n_orders_small)
    def test_many_same_price_both_sides(self, n):
        self.setUp()

        for _ in range(1, n+1):

            pbid = 1999
            qbid = random.randint(1, int(10e9))
            opbid = OrderParams(OrderSide.BID, pbid, qbid)

            pask = 2000
            qask = random.randint(1, int(10e9))
            opask = OrderParams(OrderSide.ASK, pask, qask)

            result1 : LimitResult = self.ob.process_one(opbid)
            result2 : LimitResult = self.ob.process_one(opask)

            self.assertIsInstance(result1, LimitResult)
            self.assertIsInstance(result2, LimitResult)

            self.assertTrue(result1.success())
            self.assertTrue(result1.success())

            s, q = self.ob.get_order(result1.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, opbid.quantity) 

            s, q = self.ob.get_order(result2.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, opask.quantity) 

            self.assertEqual(self.ob.best_bid(), opbid.price)
            self.assertEqual(self.ob.best_ask(), opask.price)

            self.assertEqual(self.ob.n_asks(), self.ob.n_bids())
            self.assertEqual(self.ob.n_prices(), 2)

    @given(n_orders_small)
    def test_many_different_price_both_sides(self, n):
        self.setUp()

        for i in range(1, n+1):

            pbid = random.randint(1, int(10e6))
            qbid = random.randint(1, int(10e9))
            opbid = OrderParams(OrderSide.BID, pbid, qbid)

            pask = random.randint(int(10e6)+1, int(10e7))
            qask = random.randint(1, int(10e9))
            opask = OrderParams(OrderSide.ASK, pask, qask)

            result1 : LimitResult = self.ob.process_one(opbid)
            result2 : LimitResult = self.ob.process_one(opask)

            self.assertIsInstance(result1, LimitResult)
            self.assertIsInstance(result2, LimitResult)

            self.assertTrue(result1.success())
            self.assertTrue(result1.success())

            s, q = self.ob.get_order(result1.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, opbid.quantity) 

            s, q = self.ob.get_order(result2.order_id())
            self.assertEqual(s, OrderStatus.PENDING)
            self.assertEqual(q, opask.quantity) 

            self.assertEqual(self.ob.n_asks(), self.ob.n_bids())
            self.assertEqual(self.ob.n_prices(), i*2)
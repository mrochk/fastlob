import unittest
from hypothesis import given, strategies as st, settings
import time

from pylob import OrderBook, OrderSide, OrderParams, OrderType
from pylob.orderbook.result import LimitResult
from pylob.enums import OrderStatus
from pylob.consts import MIN_VALUE, MAX_VALUE
from pylob.utils import time_int

n_orders = st.integers(min_value=1, max_value=100)

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE*2, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_expiry = st.integers(-int(2e9), int(2e9))

class TestLimitOrders(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestLimitOrders')

    @given(valid_side, valid_price, valid_qty, valid_expiry)
    def test_create(self, side, price, qty, expiry):
        '''Checking that creating an order with an expiry set in the past is not allowed.'''
        self.ob.reset()

        with self.assertRaises(ValueError): 
            # expiry not provided
            OrderParams(side, price, qty, otype=OrderType.GTD)

        if expiry <= time_int():
            # expiry must be strictly in the future
            with self.assertRaises(ValueError): 
                OrderParams(side, price, qty, otype=OrderType.GTD, expiry=expiry)
        else:
            # valid order
            gtd = OrderParams(side, price, qty, otype=OrderType.GTD, expiry=expiry)
            result : LimitResult = self.ob(gtd)
            self.assertTrue(result.success())
            self.assertTrue(self.ob.n_prices(), 1)

    def test_expired(self):
        '''Placing an order with an expiry shortly in the future, then checking that it is effectively canceled when another order is placed.'''
        self.ob.reset()

        timestamp = time_int() + 2 # 2 seconds in the future expiry
        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTD, timestamp)

        result_exp : LimitResult = self.ob(order)
        self.assertTrue(result_exp.success())
        self.assertIsInstance(result_exp, LimitResult)

        time.sleep(3)

        # at this point, first order is not valid anymore

        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTC)

        result = self.ob(order)
        self.assertTrue(result.success())
        self.assertIsInstance(result, LimitResult)

        s, q = self.ob.get_order(result_exp.order_id())
        self.assertEqual(s, OrderStatus.CANCELED)
        self.assertEqual(self.ob._bid_side.volume(), 1000)
        self.assertEqual(self.ob._bid_side._get_limit(1000).volume(), 1000)
        self.assertEqual(self.ob._bid_side._get_limit(1000).valid_orders(), 1)

    def test_expired_many(self):
        '''Placing many orders with an expiry shortly in the future, then checking that they are effectively canceled when another order is placed.'''
        self.ob.reset()

        timestamp1 = time_int() + 7 # 2 seconds in the future expiry
        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTD, timestamp1)
        result_exp1 : LimitResult = self.ob(order)
        self.assertTrue(result_exp1.success())
        self.assertIsInstance(result_exp1, LimitResult)

        timestamp2 = time_int() + 3 # 2 seconds in the future expiry
        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTD, timestamp2)
        result_exp2 : LimitResult = self.ob(order)
        self.assertTrue(result_exp2.success())
        self.assertIsInstance(result_exp2, LimitResult)

        timestamp3 = time_int() + 5 # 2 seconds in the future expiry
        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTD, timestamp3)
        result_exp3 : LimitResult = self.ob(order)
        self.assertTrue(result_exp3.success())
        self.assertIsInstance(result_exp3, LimitResult)

        timestamp3 = time_int() + 5 # 2 seconds in the future expiry
        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTD, timestamp3)
        result_exp4 : LimitResult = self.ob(order)
        self.assertTrue(result_exp4.success())
        self.assertIsInstance(result_exp4, LimitResult)

        time.sleep(10)

        # at this point, first order is not valid anymore

        order = OrderParams(OrderSide.BID, 1000, 1000, OrderType.GTC)

        result = self.ob(order)

        for r in {result_exp1, result_exp2, result_exp3}:
            s, _ = self.ob.get_order(r.order_id())
            self.assertEqual(s, OrderStatus.CANCELED)
            self.assertEqual(self.ob._bid_side.volume(), 1000)
            self.assertEqual(self.ob._bid_side._get_limit(1000).volume(), 1000)

        self.assertEqual(self.ob._bid_side._get_limit(1000).valid_orders(), 1)
        self.assertTrue(result.success())
        self.assertIsInstance(result, LimitResult)

        
import unittest
from hypothesis import given, strategies as st

from fastlob import OrderBook, OrderSide, OrderParams, todecimal
from fastlob.enums import OrderStatus
from fastlob.orderbook.result import LimitResult, MarketResult, CancelResult
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_price = st.decimals(MIN_VALUE, MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(todecimal(100), MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_side = st.sampled_from(OrderSide)

class TestCancelOrders(unittest.TestCase):
    def setUp(self):
        self.ob = OrderBook('CancelOrders')

    @given(valid_side, valid_price, valid_qty)
    def test_cancel1(self, side, price, qty):
        '''Placing a limit order and then cancelling it.'''
        self.ob.reset()

        orderp = OrderParams(side, price, qty)
        result : LimitResult = self.ob.process_one(orderp)

        self.assertIsInstance(result, LimitResult)
        self.assertTrue(result.success())

        order_id = result.order_id()

        status, qty = self.ob.get_order_status(order_id)
        self.assertEqual(status, OrderStatus.PENDING)
        self.assertEqual(qty, orderp.quantity)

        r : CancelResult = self.ob.cancel_order(order_id)
        self.assertIsInstance(r, CancelResult)

        self.assertTrue(r.success())

        self.assertEqual(self.ob.n_prices(), 0)

        status, qty = self.ob.get_order_status(order_id)
        self.assertEqual(status, OrderStatus.CANCELED)
        self.assertEqual(qty, orderp.quantity)

        match side:
            case OrderSide.BID:
                with self.assertRaises(KeyError):
                    self.ob._bid_side._get_limit(orderp.price)
            case OrderSide.ASK:
                with self.assertRaises(KeyError):
                    self.ob._ask_side._get_limit(orderp.price)

    @given(valid_side, valid_price, valid_price, valid_qty, valid_qty)
    def test_cancel2(self, side, price1, price2, qty1, qty2):
        '''Placing two limit orders and then cancelling the first one.'''
        self.ob.reset()

        order1 = OrderParams(side, price1, qty1)
        order2 = OrderParams(side, price2, qty2)

        result1 : LimitResult
        result2 : LimitResult
        result1, result2 = self.ob.process_many([order1, order2])

        self.assertIsInstance(result1, LimitResult)
        self.assertIsInstance(result2, LimitResult)
        self.assertTrue(result1.success())
        self.assertTrue(result2.success())

        if order1.price != order2.price:
            self.assertEqual(self.ob.n_asks() if side==OrderSide.ASK else self.ob.n_bids(), 2)

        id1 = result1.order_id()
        id2 = result2.order_id()
        
        r1 : CancelResult = self.ob.cancel_order(id1)
        self.assertIsInstance(r1, CancelResult)

        self.assertTrue(r1.success())

        self.assertEqual(self.ob.n_prices(), 1)

        status, qty = self.ob.get_order_status(id1)
        self.assertEqual(status, OrderStatus.CANCELED)
        self.assertEqual(qty, order1.quantity)

        if order1.price != order2.price:
            match side:
                case OrderSide.BID:
                    with self.assertRaises(KeyError):
                        self.ob._bid_side._get_limit(order1.price)
                case OrderSide.ASK:
                    with self.assertRaises(KeyError):
                        self.ob._ask_side._get_limit(order1.price)

        else:
            match side:
                case OrderSide.BID:
                    lim = self.ob._bid_side._get_limit(order1.price)
                case OrderSide.ASK:
                    lim = self.ob._ask_side._get_limit(order1.price)

            self.assertEqual(lim.valid_orders(), 1)

        
        r2 = self.ob.cancel_order(id2)
        self.assertIsInstance(r2, CancelResult)

        self.assertTrue(r2.success())

        self.assertEqual(self.ob.n_prices(), 0)

        status, qty = self.ob.get_order_status(id2)
        self.assertEqual(status, OrderStatus.CANCELED)
        self.assertEqual(qty, order2.quantity)

        match side:
            case OrderSide.BID:
                with self.assertRaises(KeyError):
                    self.ob._bid_side._get_limit(order1.price)
            case OrderSide.ASK:
                with self.assertRaises(KeyError):
                    self.ob._ask_side._get_limit(order1.price)

    @given(valid_side, valid_price, valid_qty)
    def test_cancel2(self, side, price, qty):
        '''Place then partially execute one order, and then cancel it.'''
        self.ob.reset()

        params = OrderParams(side, price, qty)
        result : LimitResult = self.ob(params)

        self.assertEqual(self.ob.best_ask() if side == OrderSide.ASK else self.ob.best_bid(), params.price)
        self.assertFalse(self.ob.get_order_status(result.order_id()) is None)

        # partially execute order

        params2 = OrderParams(OrderSide.invert(side), price, qty / 2)
        result2 : MarketResult = self.ob(params2)

        self.assertTrue(isinstance(result2, MarketResult))

        s, q = self.ob.get_order_status(result2.order_id())

        self.assertEqual(s, OrderStatus.FILLED)
        self.assertEqual(q, 0)

        s, _ = self.ob.get_order_status(result.order_id())
        self.assertEqual(s, OrderStatus.PARTIAL)

        cancelresult = self.ob.cancel_order(result.order_id())
        self.assertTrue(cancelresult.success())

        s, _ = self.ob.get_order_status(result.order_id())
        self.assertEqual(s, OrderStatus.CANCELED)

        self.assertEqual(self.ob.n_prices(), 0)
        self.assertEqual(self.ob.n_bids(), 0)
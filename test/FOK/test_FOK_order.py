import unittest
from hypothesis import given, strategies as st

from fastlob import OrderBook, OrderSide, OrderParams, OrderType
from fastlob.orderbook.result import LimitResult, MarketResult
from fastlob.enums import OrderStatus
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE-10, allow_infinity=False, allow_nan=False)

'''
There is no such thing as a FOK limit order, so it should never succeed.
'''

class TestOrders(unittest.TestCase):
    def setUp(self): self.ob = OrderBook('TestOrders')

    @given(valid_side, valid_price, valid_qty)
    def test_one_fail(self, side, price, qty):
        '''If the book is empty, then any order is a limit order, and thus if set as FOK it should fail.'''
        self.ob.reset()

        op = OrderParams(side, price, qty, otype=OrderType.FOK)
        result : LimitResult = self.ob.process_one(op)

        self.assertTrue(isinstance(result, LimitResult))
        self.assertFalse(result.success())

    @given(valid_side, valid_price, valid_qty)
    def test_one_ok(self, side, price, qty):
        '''Place a GTC limit order and then fill it fully using a FOK order.'''
        self.ob.reset()

        op = OrderParams(side, price, qty, otype=OrderType.GTC)
        resultGTC : LimitResult = self.ob.process_one(op)

        self.assertTrue(resultGTC.success())
        self.assertTrue(isinstance(resultGTC, LimitResult))

        fok = OrderParams(side, price, qty, otype=OrderType.FOK)
        resultFOK : MarketResult = self.ob.process_one(fok)

        s, q = self.ob.get_order_status(resultGTC.order_id())
        self.assertEqual(s, OrderStatus.FILLED)
        self.assertEqual(q, 0)

        s, _ = self.ob.get_order_status(resultFOK.order_id())
        self.assertEqual(s, OrderStatus.FILLED)

        self.assertTrue(resultFOK.success())
        self.assertEqual(resultFOK.orders_matched(), 1)
        self.assertEqual(resultFOK.limits_matched(), 1)
        self.assertTrue(isinstance(resultFOK, MarketResult))

    @given(valid_side, valid_price, valid_qty)
    def test_one_ok(self, side, price, qty):
        '''Place a GTC limit order and then fill it partially using a FOK order.'''
        self.ob.reset()

        qty_gtc = qty + 10

        op = OrderParams(side, price, qty_gtc, otype=OrderType.GTC)
        resultGTC : LimitResult = self.ob.process_one(op)

        self.assertTrue(resultGTC.success())
        self.assertTrue(isinstance(resultGTC, LimitResult))

        fok = OrderParams(OrderSide.invert(side), price, qty, otype=OrderType.FOK)
        resultFOK : MarketResult = self.ob.process_one(fok)

        self.assertTrue(resultFOK.success())
        self.assertEqual(resultFOK.orders_matched(), 0)
        self.assertEqual(resultFOK.limits_matched(), 0)
        self.assertTrue(isinstance(resultFOK, MarketResult))

        s, q = self.ob.get_order_status(resultGTC.order_id())
        self.assertEqual(s, OrderStatus.PARTIAL)
        self.assertEqual(q, op.quantity - fok.quantity)

        s, q = self.ob.get_order_status(resultFOK.order_id())
        self.assertEqual(s, OrderStatus.FILLED)
        self.assertEqual(q, 0)

    def test_qty_fail_bid(self):
        '''Testing the _check_bid_market_order func of the book'''
        self.ob.reset()

        limit1 = OrderParams(OrderSide.ASK, 1100, 10)
        limit2 = OrderParams(OrderSide.ASK, 1110, 10)

        r1, r2 = self.ob((limit1, limit2))

        self.assertTrue(r1.success())
        self.assertTrue(r2.success())

        # qty correct, but price should be 1110, so should fail

        fok = OrderParams(OrderSide.BID, 1105, 20, OrderType.FOK)

        fokresult = self.ob(fok)

        self.assertFalse(fokresult.success())

        # partially fill first

        fok = OrderParams(OrderSide.BID, 1100, 5, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertTrue(fokresult.success())

        # fail again because of qty
        fok = OrderParams(OrderSide.BID, 1110, 16, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertFalse(fokresult.success())

        # finally we fill the book entirely
        fok = OrderParams(OrderSide.BID, 1110, 15, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertTrue(fokresult.success())

    def test_qty_fail_ask(self):
        '''Testing the _check_ask_market_order func of the book'''
        self.ob.reset()

        limit1 = OrderParams(OrderSide.BID, 1110, 10)
        limit2 = OrderParams(OrderSide.BID, 1100, 10)

        r1, r2 = self.ob((limit1, limit2))

        self.assertTrue(r1.success())
        self.assertTrue(r2.success())

        # qty correct, but price should be 1100, so should fail

        fok = OrderParams(OrderSide.ASK, 1105, 20, OrderType.FOK)

        fokresult = self.ob(fok)

        self.assertFalse(fokresult.success())

        # partially fill first

        fok = OrderParams(OrderSide.ASK, 1105, 5, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertTrue(fokresult.success())

        # fail again because of qty
        fok = OrderParams(OrderSide.ASK, 1100, 16, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertFalse(fokresult.success())

        # finally we fill the book entirely
        fok = OrderParams(OrderSide.ASK, 1100, 15, OrderType.FOK)
        fokresult = self.ob(fok)
        self.assertTrue(fokresult.success())
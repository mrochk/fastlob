import unittest
from hypothesis import given, strategies as st

from fastlob import OrderSide
from fastlob.enums import OrderStatus
from fastlob.side import AskSide, BidSide
from fastlob.order import AskOrder, BidOrder, OrderParams
from fastlob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE-1000, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

class TestSide(unittest.TestCase):
    def setUp(self): pass

    def mkorder(self, params: OrderParams):
        return AskOrder(params) if params.side == OrderSide.ASK else BidOrder(params)

    def test_init(self):
        side = AskSide()

        self.assertTrue(side.empty())
        self.assertEqual(side.side(), OrderSide.ASK)
        self.assertEqual(side.size(), 0)
        self.assertEqual(side.volume(), 0)

        side = BidSide()

        self.assertTrue(side.empty())
        self.assertEqual(side.side(), OrderSide.BID)
        self.assertEqual(side.size(), 0)
        self.assertEqual(side.volume(), 0)

    @given(valid_side, valid_price, valid_qty)
    def test_place_order(self, s, price, qty):
        side = AskSide() if s == OrderSide.ASK else BidSide()

        params = OrderParams(s, price, qty)
        order = self.mkorder(params)

        side.place(order)

        self.assertEqual(side.volume(), order.quantity())
        self.assertEqual(side.size(), 1)
        self.assertFalse(side.empty())
        self.assertEqual(side.best().price(), order.price())
        self.assertEqual(order.status(), OrderStatus.PENDING)

    @given(valid_side, valid_price, valid_qty)
    def test_place_orders(self, s, price, qty):
        side = AskSide() if s == OrderSide.ASK else BidSide()

        for i in range(100):
            params = OrderParams(s, price, qty)
            order = self.mkorder(params)
            side.place(order)

        self.assertEqual(side.volume(), order.quantity()*100)
        self.assertEqual(side.best().volume(), order.quantity()*100)
        self.assertEqual(side.size(), 1)
        self.assertFalse(side.empty())
        self.assertEqual(side.best().price(), order.price())
        self.assertEqual(side.best().valid_orders(), 100)

    def test_ask_best(self):
        side = AskSide()

        params = OrderParams(OrderSide.ASK, 200, 10)
        order = self.mkorder(params)

        side.place(order)

        params = OrderParams(OrderSide.ASK, 100, 10)
        order = self.mkorder(params)
        
        side.place(order)

        self.assertEqual(side.best().price(), 100)
        self.assertEqual(side.size(), 2)

    def test_ask_best_2(self):
        side = AskSide()

        params = OrderParams(OrderSide.ASK, 100, 10)
        order = self.mkorder(params)

        side.place(order)

        params = OrderParams(OrderSide.ASK, 200, 10)
        order = self.mkorder(params)
        
        side.place(order)

        self.assertEqual(side.best().price(), 100)
        self.assertEqual(side.size(), 2)

    def test_bid_best(self):
        side = BidSide()

        params = OrderParams(OrderSide.BID, 200, 10)
        order = self.mkorder(params)

        side.place(order)

        params = OrderParams(OrderSide.BID, 100, 10)
        order = self.mkorder(params)
        
        side.place(order)

        self.assertEqual(side.best().price(), 200)
        self.assertEqual(side.size(), 2)

    def test_bid_best_2(self):
        side = BidSide()

        params = OrderParams(OrderSide.BID, 100, 10)
        order = self.mkorder(params)

        side.place(order)

        params = OrderParams(OrderSide.BID, 200, 10)
        order = self.mkorder(params)
        
        side.place(order)

        self.assertEqual(side.best().price(), 200)
        self.assertEqual(side.size(), 2)

    @given(valid_side, valid_price, valid_qty)
    def test_cancel_order(self, s, price, qty):
        side = AskSide() if s == OrderSide.ASK else BidSide()

        params = OrderParams(s, price, qty)
        order = self.mkorder(params)
        side.place(order)

        side.cancel_order(order)

        self.assertTrue(side.empty())
        self.assertEqual(order.status(), OrderStatus.CANCELED)

    @given(valid_side, valid_price, valid_qty)
    def test_cancel_orders(self, s, price, qty):
        side = AskSide()
        orders = list()

        for i in range(100):
            params = OrderParams(s, price+i, qty)
            order = self.mkorder(params)
            side.place(order)
            orders.append(order)

        self.assertEqual(side.size(), 100)
        self.assertEqual(side.volume(), order.quantity()*100)

        vol = side.volume()

        for i in range(100):
            order = orders[i]
            side.cancel_order(order)

            self.assertEqual(side.size(), 100-i-1)
            self.assertEqual(side.volume(), vol - (order.quantity()*(i+1)))
            self.assertEqual(order.status(), OrderStatus.CANCELED)

        self.assertTrue(side.empty())
        self.assertEqual(side.volume(), 0)

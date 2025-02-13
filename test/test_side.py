import unittest
from hypothesis import given, strategies as st

from pylob import OrderSide
from pylob.enums import OrderStatus
from pylob.side import AskSide, BidSide
from pylob.order import AskOrder, BidOrder, OrderParams
from pylob.consts import MIN_VALUE, MAX_VALUE

valid_side = st.sampled_from(OrderSide)
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

class TestSide(unittest.TestCase):
    def setUp(self): pass

    def create_side(self, s : OrderSide):
        return AskSide() if s == OrderSide.ASK else BidSide()

    @given(valid_side)
    def test_init(self, s):
        side = self.create_side(s)

        self.assertEqual(side.side(), s)
        self.assertEqual(side.volume(), 0)
        self.assertEqual(side.size(), 0)
        self.assertTrue(side.empty(), 0)

    @given(valid_side, valid_price)
    def test_new_price(self, s, price):
        side = self.create_side(s)
        side._new_price(price)

        self.assertTrue(side._price_exists(price))

    @given(valid_side, valid_price, valid_price, valid_qty, valid_qty)
    def test_place(self, s, price1, price2, qty1, qty2):
        side = self.create_side(s)

        params = OrderParams(s, price1, qty1)

        order1 = AskOrder(params) if s == OrderSide.ASK else BidOrder(params)

        self.assertEqual(order1.status(), OrderStatus.CREATED)

        side.place(order1)

        self.assertEqual(order1.status(), OrderStatus.PENDING)
        self.assertTrue(side._price_exists(order1.price()))
        self.assertEqual(side.volume(), order1.quantity())
        self.assertEqual(side.size(), 1)

        params = OrderParams(s, price2, qty2)

        order2 = AskOrder(params) if s == OrderSide.ASK else BidOrder(params)

        self.assertEqual(order2.status(), OrderStatus.CREATED)

        side.place(order2)

        self.assertEqual(order2.status(), OrderStatus.PENDING)
        self.assertTrue(side._price_exists(order2.price()))
        self.assertEqual(side.volume(), order2.quantity() + order1.quantity())
        self.assertTrue(side.size() in {1, 2})

    @given(valid_side, valid_price, valid_price, valid_qty, valid_qty)
    def test_cancel(self, s, price1, price2, qty1, qty2):
        side = self.create_side(s)
        params = OrderParams(s, price1, qty1)
        order1 = AskOrder(params) if s == OrderSide.ASK else BidOrder(params)
        side.place(order1)
        params = OrderParams(s, price2, qty2)
        order2 = AskOrder(params) if s == OrderSide.ASK else BidOrder(params)
        side.place(order2)

        side.cancel_order(order1)
        self.assertEqual(order1.status(), OrderStatus.CANCELED)
        self.assertEqual(side.volume(), order2.quantity())
        self.assertEqual(side.size(), 1)

        side.cancel_order(order2)
        self.assertEqual(order2.status(), OrderStatus.CANCELED)
        self.assertEqual(side.volume(), 0)
        self.assertEqual(side.size(), 0)

        self.assertFalse(side._price_exists(order1.price()))
        self.assertFalse(side._price_exists(order2.price()))

        with self.assertRaises(KeyError): side._get_limit(order1.price())

        with self.assertRaises(KeyError): side._get_limit(order2.price())
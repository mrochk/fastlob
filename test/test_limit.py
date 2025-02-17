import unittest
from decimal import Decimal
from hypothesis import given, strategies as st
import secrets

from pylob.limit import Limit
from pylob.enums import OrderSide, OrderStatus
from pylob.order import OrderParams, BidOrder, AskOrder
from pylob.consts import MIN_VALUE, MAX_VALUE
from pylob.utils import todecimal

valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_side = st.sampled_from(OrderSide)
valid_order_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
random_uuid = st.sampled_from([secrets.token_urlsafe(8) for _ in range(1000)])

class TestLimit(unittest.TestCase):
    def setUp(self): pass

    @given(valid_price)
    def test_init(self, price):
        price = todecimal(price)
        limit = Limit(price)

        self.assertEqual(limit.price(), price)
        self.assertEqual(limit.volume(), Decimal(0))
        self.assertEqual(limit.valid_orders(), 0)

    def create_order(self, price, side, qty):
        orderparams = OrderParams(side, price, qty)
        order = BidOrder(orderparams) if side == OrderSide.BID else AskOrder(orderparams)
        return order

    @given(valid_price, valid_side, valid_order_qty)
    def test_add_order(self, price, side, qty):
        price = todecimal(price)
        order = self.create_order(price, side, qty)
        limit = Limit(price)
        limit.enqueue(order)
        self.assertEqual(limit.volume(), order.quantity())
        self.assertEqual(limit.valid_orders(), 1)
        self.assertEqual(limit.next_order(), order)

    @given(valid_price, valid_side, valid_order_qty)
    def test_get_next_order(self, price, side, qty):
        price = todecimal(price)
        order1 = self.create_order(price, side, qty)
        order2 = self.create_order(price, side, qty)
        limit = Limit(price)
        limit.enqueue(order1)
        limit.enqueue(order2)
        self.assertEqual(limit.next_order(), order1)

    @given(valid_price, valid_side, valid_order_qty, valid_order_qty)
    def test_delete_next_order(self, price, side, qty1, qty2):
        price = todecimal(price)
        order1 = self.create_order(price, side, qty1)
        order2 = self.create_order(price, side, qty2)
        limit = Limit(price)
        limit.enqueue(order1)
        limit.enqueue(order2)
        limit.pop_next_order()
        self.assertEqual(limit.next_order(), order2)
        self.assertEqual(limit.volume(), order2.quantity())
        self.assertEqual(limit.valid_orders(), 1)

    @given(valid_price, valid_side, valid_order_qty)
    def test_cancel_order(self, price, side, qty):
        price = todecimal(price)
        order = self.create_order(price, side, qty)
        limit = Limit(price)
        limit.enqueue(order)
        limit.cancel_order(order)
        self.assertEqual(order.status(), OrderStatus.CANCELED)
        self.assertEqual(limit.volume(), Decimal(0))
        self.assertEqual(limit.valid_orders(), 0)
        self.assertTrue(limit.empty())

    @given(valid_price, valid_side, valid_order_qty, valid_order_qty)
    def test_prune_canceled_orders(self, price, side, qty1, qty2):
        price = todecimal(price)
        order1 = self.create_order(price, side, qty1)
        order2 = self.create_order(price, side, qty2)
        limit = Limit(price)
        limit.enqueue(order1)
        limit.enqueue(order2)
        limit.cancel_order(order1)
        limit._prune_canceled()
        self.assertEqual(limit.next_order(), order2)
        self.assertEqual(limit.volume(), order2.quantity())
        self.assertEqual(limit.valid_orders(), 1)

    @given(valid_price, valid_side, valid_order_qty)
    def test_empty(self, price, side, qty):
        price = todecimal(price)
        limit = Limit(price)
        self.assertTrue(limit.empty())
        order = self.create_order(price, side, qty)
        limit.enqueue(order)
        self.assertFalse(limit.empty())
        limit.pop_next_order()
        self.assertTrue(limit.empty())

import unittest
from decimal import Decimal
from hypothesis import given
import hypothesis.strategies as st
import time

from pylob import OrderParams
from pylob.consts import MAX_VALUE, MIN_VALUE
from pylob.enums import OrderSide, OrderType, OrderStatus
from pylob.utils import todecimal
from pylob.order import Order, BidOrder, AskOrder

# Strategies for generating valid values
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_quantity = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_fill = st.decimals(min_value=MIN_VALUE*2, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_order_side = st.sampled_from(OrderSide)
valid_order_type = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry = st.one_of(st.none(), st.floats(min_value=0, allow_nan=False, allow_infinity=False))

class TestOrder(unittest.TestCase):
    @given(valid_order_side, valid_price, valid_quantity, valid_order_type, valid_expiry)
    def test_order_initialization(self, side, price, quantity, type, expiry):
        params = OrderParams(side, price, quantity, type, expiry)
        order = BidOrder(params) if side == OrderSide.BID else AskOrder(params)

        self.assertEqual(order.price(), todecimal(price))
        self.assertEqual(order.quantity(), todecimal(quantity))
        self.assertEqual(order.otype(), type)
        self.assertEqual(order.status(), OrderStatus.CREATED)

    @given(valid_price, valid_fill)
    def test_order_fill(self, price, quantity):
        params = OrderParams(OrderSide.BID, price, quantity, OrderType.GTC)
        order = BidOrder(params)

        partial_fill = todecimal(quantity / 2)
        order.fill(partial_fill)
        self.assertEqual(order.status(), OrderStatus.PARTIAL)
        self.assertEqual(order.quantity(), todecimal(quantity) - partial_fill)

        order.fill(quantity)
        self.assertEqual(order.status(), OrderStatus.FILLED)
        self.assertEqual(order.quantity(), Decimal(0))

    def test_order_status_transitions(self):
        params = OrderParams(OrderSide.BID, Decimal("10"), Decimal("5"), OrderType.GTC)
        order = BidOrder(params)

        order.set_status(OrderStatus.CANCELED)
        self.assertTrue(order.canceled())
        self.assertFalse(order.valid())

    def test_order_equality(self):
        params1 = OrderParams(OrderSide.BID, Decimal("10"), Decimal("5"), OrderType.GTC)
        params2 = OrderParams(OrderSide.BID, Decimal("10"), Decimal("5"), OrderType.GTC)
        order1 = BidOrder(params1)
        order2 = BidOrder(params2)

        self.assertNotEqual(order1, order2)  # Different unique IDs

import unittest
from decimal import Decimal
from hypothesis import given
import hypothesis.strategies as st
import time

from pylob import OrderParams
from pylob.consts import MIN_VALUE, MAX_VALUE
from pylob.enums import OrderSide, OrderType
from pylob.utils import todecimal

# Strategies for generating valid values
valid_price = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_quantity = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_nan=False, allow_infinity=False)
valid_order_side = st.sampled_from(OrderSide)
valid_order_type = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry = st.one_of(st.none(), st.floats(min_value=0, allow_nan=False, allow_infinity=False))


class TestOrderParams(unittest.TestCase):
    @given(valid_order_side, valid_price, valid_quantity, valid_order_type, valid_expiry)
    def test_order_params_valid(self, side, price, quantity, type, expiry):
        if type == OrderType.GTD and (not expiry or expiry <= int(time.time())):
            with self.assertRaises(ValueError): OrderParams(side, price, quantity, type, expiry)
            return

        order = OrderParams(side, price, quantity, type, expiry)
        self.assertEqual(order.side, side)
        self.assertEqual(order.price, todecimal(price))
        self.assertEqual(order.quantity, todecimal(quantity))
        self.assertEqual(order.otype, type)

    def test_invalid_side(self):
        with self.assertRaises(TypeError):
            OrderParams("invalid", Decimal("10"), Decimal("1"))

    def test_invalid_price(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, "not a decimal", Decimal("1"))
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, Decimal("0"), Decimal("1"))
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, Decimal("-1"), Decimal("1"))

    def test_invalid_quantity(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, Decimal("10"), "not a decimal")
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, Decimal("10"), Decimal("0"))
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, Decimal("10"), Decimal("-1"))
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, Decimal("10"), MAX_VALUE + 10)
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, MAX_VALUE + 10, Decimal("10"))

    def test_invalid_order_type(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, Decimal("10"), Decimal("1"), "invalid_type")

    def test_invalid_expiry(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, Decimal("10"), Decimal("1"), OrderType.GTC, "invalid")

    @given(valid_order_side, valid_price, valid_quantity, valid_order_type)
    def test_unwrap(self, side, price, quantity, type):
        order = OrderParams(side, price, quantity, type)
        self.assertTupleEqual(order.unwrap(), (todecimal(price), todecimal(quantity), type, None))

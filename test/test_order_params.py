import unittest
from decimal import Decimal
from pylob.enums import OrderSide, OrderType
from pylob.utils import todecimal
from pylob.order import OrderParams


class TestOrderParams(unittest.TestCase):
    def test_order_params_creation(self):
        order = OrderParams(OrderSide.BID, 100.5, 10)
        self.assertEqual(order.side, OrderSide.BID)
        self.assertEqual(order.price, todecimal(100.5))
        self.assertEqual(order.quantity, todecimal(10))
        self.assertEqual(order.type, OrderType.GTC)
        self.assertIsNone(order.expiry)

    def test_order_params_with_optional_expiry(self):
        order = OrderParams(OrderSide.ASK, 50.25, 5,
                            OrderType.FOK, 1650000000.0)
        self.assertEqual(order.side, OrderSide.ASK)
        self.assertEqual(order.price, todecimal(50.25))
        self.assertEqual(order.quantity, todecimal(5))
        self.assertEqual(order.type, OrderType.FOK)
        self.assertEqual(order.expiry, 1650000000.0)

    def test_order_params_invalid_side(self):
        with self.assertRaises(TypeError):
            OrderParams("INVALID", 100, 10)

    def test_order_params_invalid_price(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, "abc", 10)
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.BID, -100, 10)

    def test_order_params_invalid_quantity(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, 100, "xyz")
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 100, -5)

    def test_order_params_invalid_type(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.BID, 100, 10, "LIMIT")

    def test_order_params_invalid_expiry(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC, "tomorrow")

    def test_order_params_unwrap(self):
        order = OrderParams(OrderSide.BID, 99.99, 20, OrderType.GTC, None)
        self.assertEqual(order.unwrap(), (Decimal("99.99"),
                         Decimal("20"), OrderType.GTC, None))

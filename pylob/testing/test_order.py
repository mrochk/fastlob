import unittest
from decimal import Decimal

from ..order import OrderType, AskOrder, BidOrder

class TestOrder(unittest.TestCase):
    def test_decimal(self):
        order = AskOrder(
            price=10,
            quantity=10,
            type=OrderType.FOK,
        )

        self.assertEqual(order.price, Decimal('10.00'))
        self.assertEqual(order.quantity, Decimal('10.00'))

        self.assertEqual(str(order.price), '10.00' )
        self.assertEqual(str(order.quantity), '10.00' )

        self.assertNotEqual(str(order.price), '10.000')
        self.assertNotEqual(str(order.quantity), '10.000')

        self.assertNotEqual(str(order.price), '10.0')
        self.assertNotEqual(str(order.quantity), '10.0')
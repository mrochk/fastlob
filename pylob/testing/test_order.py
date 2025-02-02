import unittest
from decimal import Decimal

from pylob import OrderSide, OrderType 
from pylob.order import AskOrder, BidOrder

class TestOrder(unittest.TestCase):
    def test_decimal(self):
        order = AskOrder(price=10, quantity=10, type=OrderType.FOK)

        self.assertEqual(order.price(), Decimal('10.00'))
        self.assertEqual(order.quantity(), Decimal('10.00'))

        self.assertEqual(str(order.price()), '10.00')
        self.assertEqual(str(order.quantity()), '10.00')

        self.assertNotEqual(str(order.price()), '10.000')
        self.assertNotEqual(str(order.quantity()), '10.000')

        self.assertNotEqual(str(order.price()), '10.0')
        self.assertNotEqual(str(order.quantity()), '10.0')
    
    def test_order_initialization(self):
        order = BidOrder(price=100.5, quantity=50.25, type=OrderType.GTC)
        self.assertIsInstance(order, BidOrder)
        self.assertEqual(order.price(), Decimal('100.5'))
        self.assertEqual(order.quantity(), Decimal('50.25'))
        self.assertEqual(order.type(), OrderType.GTC)
        self.assertEqual(order.side(), OrderSide.BID)
    
    def test_order_side(self):
        bid = BidOrder(price=50, quantity=10, type=OrderType.FOK)
        ask = AskOrder(price=60, quantity=15, type=OrderType.GTC)
        
        self.assertEqual(bid.side(), OrderSide.BID)
        self.assertEqual(ask.side(), OrderSide.ASK)
    
    def test_partial_fill(self):
        order = AskOrder(price=20, quantity=10, type=OrderType.GTC)
        order.partial_fill(Decimal('3.5'))
        self.assertEqual(order.quantity(), Decimal('6.5'))
        
        order.partial_fill(Decimal('6.5'))
        self.assertEqual(order.quantity(), Decimal('0'))
    
    def test_order_equality(self):
        order1 = BidOrder(price=30, quantity=5, type=OrderType.GTD)
        order2 = BidOrder(price=30, quantity=5, type=OrderType.GTD)
        self.assertNotEqual(order1, order2)  # Different UUIDs should make them different
    
    def test_expiry(self):
        order = AskOrder(price=25, quantity=10, type=OrderType.GTD, expiry=1672531199.0)
        self.assertEqual(order.expiry(), 1672531199.0)
    
    def test_order_repr(self):
        order = BidOrder(price=42, quantity=10, type=OrderType.FOK)
        self.assertTrue(order.__repr__().startswith("BidOrder(id="))
    
    def test_invalid_partial_fill(self):
        order = BidOrder(price=50, quantity=5, type=OrderType.FOK)
        with self.assertRaises(ValueError):
            order.partial_fill(Decimal('10'))  # Should not allow filling more than available
    
    def test_zero_partial_fill(self):
        order = AskOrder(price=30, quantity=5, type=OrderType.GTC)
        order.partial_fill(Decimal('0'))
        self.assertEqual(order.quantity(), Decimal('5'))  # Should remain unchanged
    
    def test_negative_price(self):
        with self.assertRaises(ValueError):
            BidOrder(price=-10, quantity=5, type=OrderType.GTD)  # Price should not be negative
    
    def test_large_quantity(self):
        order = AskOrder(price=100, quantity=Decimal('1000000'), type=OrderType.GTC)
        self.assertEqual(order.quantity(), Decimal('1000000'))  # Large quantity should be handled correctly
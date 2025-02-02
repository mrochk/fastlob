import unittest
from decimal import Decimal
from pylob import OrderType, OrderSide
from pylob.order import AskOrder, BidOrder
from pylob.limit import Limit

class TestLimit(unittest.TestCase):
    def setUp(self):
        self.limit = Limit(price=100, side=OrderSide.BID)
        self.order1 = BidOrder(price=100, quantity=10, type=OrderType.GTC)
        self.order2 = BidOrder(price=100, quantity=5, type=OrderType.FOK)
    
    def test_limit_initialization(self):
        self.assertEqual(self.limit.price(), Decimal('100'))
        self.assertEqual(self.limit.side(), OrderSide.BID)
        self.assertEqual(self.limit.volume(), Decimal('0'))
        self.assertEqual(self.limit.size(), 0)
    
    def test_add_order(self):
        self.limit.add_order(self.order1)
        self.assertEqual(self.limit.size(), 1)
        self.assertEqual(self.limit.volume(), Decimal('10'))
        
        self.limit.add_order(self.order2)
        self.assertEqual(self.limit.size(), 2)
        self.assertEqual(self.limit.volume(), Decimal('15'))
    
    def test_order_exists(self):
        self.limit.add_order(self.order1)
        self.assertTrue(self.limit.order_exists(self.order1.id()))
        self.assertFalse(self.limit.order_exists(self.order2.id()))
    
    def test_get_order(self):
        self.limit.add_order(self.order1)
        self.assertEqual(self.limit.get_order(self.order1.id()), self.order1)
        
        with self.assertRaises(ValueError):
            self.limit.get_order(self.order2.id())
    
    def test_next_order(self):
        self.limit.add_order(self.order1)
        self.limit.add_order(self.order2)
        self.assertEqual(self.limit.next_order(), self.order1)
        
        self.limit.pop_next_order()
        self.assertEqual(self.limit.next_order(), self.order2)
    
    def test_pop_next_order(self):
        self.limit.add_order(self.order1)
        self.limit.add_order(self.order2)
        self.limit.pop_next_order()
        self.assertEqual(self.limit.size(), 1)
        self.assertEqual(self.limit.volume(), Decimal('5'))
        
        self.limit.pop_next_order()
        self.assertEqual(self.limit.size(), 0)
        self.assertEqual(self.limit.volume(), Decimal('0'))
        
        with self.assertRaises(ValueError):
            self.limit.pop_next_order()
    
    def test_add_order_sanity_check(self):
        with self.assertRaises(ValueError):
            self.limit.add_order(AskOrder(price=100, quantity=10, type=OrderType.GTC))
        
        with self.assertRaises(ValueError):
            self.limit.add_order(BidOrder(price=101, quantity=10, type=OrderType.GTC))
    
    def test_limit_repr(self):
        self.limit.add_order(self.order1)
        self.assertTrue(self.limit.__repr__().startswith("Limit(price=100"))
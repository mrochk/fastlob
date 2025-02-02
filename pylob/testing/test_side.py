import unittest
from decimal import Decimal
from pylob import OrderSide, OrderType
from pylob.order import BidOrder, AskOrder
from pylob.side import BidSide, AskSide

class TestSide(unittest.TestCase):
    def setUp(self):
        self.bid_side = BidSide()
        self.ask_side = AskSide()
        self.bid_side.add_limit(100)
        self.ask_side.add_limit(110)
        self.order1 = BidOrder(price=100, quantity=10, type=OrderType.GTC)
        self.order2 = AskOrder(price=110, quantity=5, type=OrderType.FOK)

    def test_side_initialization(self):
        self.assertEqual(self.bid_side.side(), OrderSide.BID)
        self.assertEqual(self.ask_side.side(), OrderSide.ASK)
        self.assertEqual(self.bid_side.size(), 1)
        self.assertEqual(self.ask_side.size(), 1)

    def test_add_limit(self):
        self.bid_side.add_limit(90)
        self.assertTrue(90 in self.bid_side.prices())
        self.ask_side.add_limit(120)
        self.assertTrue(120 in self.ask_side.prices())

    def test_limit_exist(self):
        self.assertTrue(self.bid_side.limit_exists(100))
        self.assertFalse(self.bid_side.limit_exists(105))

    def test_add_order(self):
        self.bid_side.add_order(self.order1)
        self.assertEqual(self.bid_side.best().volume(), Decimal('10'))
        self.ask_side.add_order(self.order2)
        self.assertEqual(self.ask_side.best().volume(), Decimal('5'))

    def test_remove_limit(self):
        self.bid_side.remove_limit(100)
        self.assertFalse(self.bid_side.limit_exists(100))
        
        self.ask_side.remove_limit(110)
        self.assertFalse(self.ask_side.limit_exists(110))
        
    def test_best_limit(self):
        self.assertEqual(self.bid_side.best().price(), Decimal('100'))
        self.assertEqual(self.ask_side.best().price(), Decimal('110'))
    
    def test_volume(self):
        self.bid_side.add_order(self.order1)
        self.ask_side.add_order(self.order2)
        self.assertEqual(self.bid_side.volume(), Decimal('10'))
        self.assertEqual(self.ask_side.volume(), Decimal('5'))
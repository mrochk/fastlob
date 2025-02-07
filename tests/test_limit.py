import unittest
from decimal import Decimal
from pylob.enums import OrderSide, OrderStatus
from pylob.order import BidOrder, AskOrder
from pylob.limit import Limit  
from pylob.order import OrderParams

class TestLimit(unittest.TestCase):
    def setUp(self):
        self.limit_bid = Limit(Decimal(100), OrderSide.BID)
        self.limit_ask = Limit(Decimal(150), OrderSide.ASK)
        self.order1 = BidOrder(OrderParams(OrderSide.BID, 100, 10))
        self.order2 = AskOrder(OrderParams(OrderSide.ASK, 150, 5))

    def test_limit_initialization(self):
        self.assertEqual(self.limit_bid.price(), Decimal(100))
        self.assertEqual(self.limit_bid.side(), OrderSide.BID)
        self.assertEqual(self.limit_bid.volume(), Decimal(0))
        self.assertTrue(self.limit_bid.empty())

    def test_add_order(self):
        self.limit_bid.add_order(self.order1)
        self.assertEqual(self.limit_bid.volume(), Decimal(10))
        self.assertEqual(self.limit_bid.size(), 1)
        self.assertFalse(self.limit_bid.empty())
        self.assertEqual(self.order1.status(), OrderStatus.IN_LINE)

    def test_order_exists(self):
        self.limit_bid.add_order(self.order1)
        self.assertTrue(self.limit_bid.order_exists(self.order1.id()))
        self.assertFalse(self.limit_bid.order_exists(9999))

    def test_get_order(self):
        self.limit_bid.add_order(self.order1)
        self.assertEqual(self.limit_bid.get_order(self.order1.id()), self.order1)

    def test_next_order(self):
        self.limit_bid.add_order(self.order1)
        self.assertEqual(self.limit_bid.next_order(), self.order1)

    def test_pop_next_order(self):
        self.limit_bid.add_order(self.order1)
        order = self.limit_bid.pop_next_order()
        self.assertEqual(order, self.order1)
        self.assertTrue(self.limit_bid.empty())

    def test_partial_fill_next(self):
        self.limit_bid.add_order(self.order1)
        self.limit_bid.partial_fill_next(5)
        self.assertEqual(self.order1.quantity(), Decimal(5))
        self.assertEqual(self.limit_bid.volume(), Decimal(5))
        self.assertEqual(self.order1.status(), OrderStatus.PARTIAL)

    def test_full_fill_next(self):
        self.limit_ask.add_order(self.order2)
        self.limit_ask.partial_fill_next(5)
        self.assertEqual(self.order2.quantity(), Decimal(0))
        self.assertEqual(self.limit_ask.volume(), Decimal(0))
        self.assertEqual(self.order2.status(), OrderStatus.FILLED)

    def test_repr(self):
        self.assertTrue(repr(self.limit_bid).startswith("BIDLimit"))
        self.assertTrue(repr(self.limit_ask).startswith("ASKLimit"))


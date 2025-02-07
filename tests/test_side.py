import unittest
from decimal import Decimal
from pylob.enums import OrderSide, OrderType
from pylob.order import BidOrder, AskOrder
from pylob.side import BidSide, AskSide
from pylob.limit import Limit
from pylob.order import OrderParams

class TestBidSide(unittest.TestCase):
    def setUp(self):
        self.side = BidSide()

    def test_add_limit(self):
        self.side.add_limit(Decimal("100.5"))
        self.assertTrue(self.side.price_exists(Decimal("100.5")))

    def test_place_order(self):
        order_params = OrderParams(OrderSide.BID, 100.5, 10, OrderType.GTC)
        order = BidOrder(order_params)
        self.side.add_limit(order.price())
        self.side.place_order(order)
        self.assertEqual(self.side.get_order(order.id()), order)

    def test_remove_order(self):
        order_params = OrderParams(OrderSide.BID, 100.5, 10, OrderType.GTC)
        order = BidOrder(order_params)
        self.side.add_limit(order.price())
        self.side.place_order(order)
        self.side.remove_order(order.id())
        self.assertFalse(order.id() in self.side._orders)

    def test_best_limit(self):
        self.side.add_limit(Decimal("100"))
        self.side.add_limit(Decimal("101"))
        self.assertEqual(self.side.best().price(), Decimal("101"))

class TestAskSide(unittest.TestCase):
    def setUp(self):
        self.side = AskSide()

    def test_add_limit(self):
        self.side.add_limit(Decimal("200.5"))
        self.assertTrue(self.side.price_exists(Decimal("200.5")))

    def test_place_order(self):
        order_params = OrderParams(OrderSide.ASK, 200.5, 15, OrderType.GTC)
        order = AskOrder(order_params)
        self.side.add_limit(order.price())
        self.side.place_order(order)
        self.assertEqual(self.side.get_order(order.id()), order)

    def test_remove_order(self):
        order_params = OrderParams(OrderSide.ASK, 200.5, 15, OrderType.GTC)
        order = AskOrder(order_params)
        self.side.add_limit(order.price())
        self.side.place_order(order)
        self.side.remove_order(order.id())
        self.assertFalse(order.id() in self.side._orders)

    def test_best_limit(self):
        self.side.add_limit(Decimal("199"))
        self.side.add_limit(Decimal("198"))
        self.assertEqual(self.side.best().price(), Decimal("198"))

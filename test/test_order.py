import unittest
from decimal import Decimal
from pylob.enums import OrderSide, OrderType, OrderStatus
from pylob.order import OrderParams
from pylob.order import Order, BidOrder, AskOrder


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.params_bid = OrderParams(
            OrderSide.BID, 100, 10, OrderType.GTC, None)
        self.params_ask = OrderParams(
            OrderSide.ASK, 150, 5, OrderType.GTD, 1700000000.0)
        self.bid_order = BidOrder(self.params_bid)
        self.ask_order = AskOrder(self.params_ask)

    def test_order_initialization(self):
        self.assertEqual(self.bid_order.price(), Decimal(100))
        self.assertEqual(self.bid_order.quantity(), Decimal(10))
        self.assertEqual(self.bid_order.type(), OrderType.GTC)
        self.assertEqual(self.bid_order.expiry(), None)
        self.assertEqual(self.bid_order.side(), OrderSide.BID)
        self.assertEqual(self.bid_order.status(), OrderStatus.CREATED)

    def test_order_fill_partial(self):
        self.bid_order.fill(5)
        self.assertEqual(self.bid_order.quantity(), Decimal(5))
        self.assertEqual(self.bid_order.status(), OrderStatus.PARTIAL)

    def test_order_fill_complete(self):
        self.ask_order.fill(5)
        self.assertEqual(self.ask_order.quantity(), Decimal(0))
        self.assertEqual(self.ask_order.status(), OrderStatus.FILLED)

    def test_order_equality(self):
        another_bid = BidOrder(self.params_bid)
        # IDs should be unique
        self.assertNotEqual(self.bid_order, another_bid)

    def test_order_representation(self):
        self.assertTrue(repr(self.bid_order).startswith("BidOrder"))
        self.assertTrue(repr(self.ask_order).startswith("AskOrder"))

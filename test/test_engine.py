import unittest
from decimal import Decimal
from collections import defaultdict
from pylob.enums import OrderSide, OrderType
from pylob.order import BidOrder, AskOrder
from pylob.side import BidSide, AskSide
from pylob.order import OrderParams
from pylob.engine import PlaceResult, ExecResult
from pylob.engine import place, execute


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.bid_side = BidSide()
        self.ask_side = AskSide()

    def test_place_bid_order(self):
        order_params = OrderParams(OrderSide.BID, 101, 5, OrderType.GTC)
        order = BidOrder(order_params)
        result = place(order, self.bid_side)
        self.assertTrue(result.success)
        self.assertEqual(result.identifier, order.id())
        self.assertTrue(self.bid_side.price_exists(Decimal("101")))

    def test_place_ask_order(self):
        order_params = OrderParams(OrderSide.ASK, 99, 5, OrderType.GTC)
        order = AskOrder(order_params)
        result = place(order, self.ask_side)
        self.assertTrue(result.success)
        self.assertEqual(result.identifier, order.id())
        self.assertTrue(self.ask_side.price_exists(Decimal("99")))

    def test_execute_order_full_fill(self):
        bid_order_params = OrderParams(OrderSide.BID, 100, 10, OrderType.GTC)
        bid_order = BidOrder(bid_order_params)
        place(bid_order, self.bid_side)

        ask_order_params = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC)
        ask_order = AskOrder(ask_order_params)

        result = execute(ask_order, self.bid_side)
        self.assertTrue(result._success)
        self.assertEqual(result.orders_matched, 1)
        self.assertEqual(result.limits_matched, 1)
        self.assertEqual(
            result.execution_prices[Decimal("100")], Decimal("10"))

    def test_execute_order_partial_fill(self):
        bid_order_params = OrderParams(OrderSide.BID, 100, 10, OrderType.GTC)
        bid_order = BidOrder(bid_order_params)
        place(bid_order, self.bid_side)

        ask_order_params = OrderParams(OrderSide.ASK, 100, 5, OrderType.GTC)
        ask_order = AskOrder(ask_order_params)

        result = execute(ask_order, self.bid_side)

        self.assertTrue(result._success)
        self.assertEqual(result.orders_matched, 0)
        self.assertEqual(result.limits_matched, 0)
        self.assertEqual(result.execution_prices[Decimal("100")], Decimal("5"))
        self.assertEqual(self.bid_side.best().volume(), Decimal("5"))

    def test_execute_order_insufficient_volume(self):
        ask_order_params = OrderParams(OrderSide.ASK, 100, 10, OrderType.GTC)
        ask_order = AskOrder(ask_order_params)
        result = execute(ask_order, self.bid_side)
        self.assertFalse(result._success)
        self.assertIn("order quantity bigger than side volume", result._message)

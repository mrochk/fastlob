import unittest
from decimal import Decimal
from pylob.enums import OrderSide, OrderType
from pylob.order import OrderParams
from pylob.orderbook import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook("TestBook")

    def test_place_bid_order(self):
        order_params = OrderParams(
            OrderSide.BID, Decimal("100.5"), 10, OrderType.GTC)
        result = self.order_book.process_one(order_params)
        self.assertTrue(result._success)
        self.assertEqual(self.order_book.best_bid(), Decimal("100.5"))
        self.assertEqual(self.order_book.nbids(), 1)

    def test_place_ask_order(self):
        order_params = OrderParams(
            OrderSide.ASK, Decimal("101.0"), 5, OrderType.GTC)
        result = self.order_book.process_one(order_params)
        self.assertTrue(result._success)
        self.assertEqual(self.order_book.best_ask(), Decimal("101.0"))
        self.assertEqual(self.order_book.nasks(), 1)

    def test_execute_market_order(self):
        bid_params = OrderParams(
            OrderSide.BID, Decimal("100.5"), 10, OrderType.GTC)
        ask_params = OrderParams(
            OrderSide.ASK, Decimal("100.5"), 10, OrderType.GTC)

        self.order_book.process_one(bid_params)
        result = self.order_book.process_one(ask_params)

        self.assertTrue(result._success)
        self.assertEqual(result.orders_matched, 1)
        self.assertEqual(result.limits_matched, 1)
        self.assertEqual(self.order_book.nprices(), 0)

    def test_spread_calculation(self):
        self.order_book.process_one(OrderParams(
            OrderSide.BID, Decimal("100.0"), 10, OrderType.GTC))
        self.order_book.process_one(OrderParams(
            OrderSide.ASK, Decimal("102.0"), 10, OrderType.GTC))
        self.assertEqual(self.order_book.spread(), Decimal("2.0"))

    def test_midprice_calculation(self):
        self.order_book.process_one(OrderParams(
            OrderSide.BID, Decimal("100.0"), 10, OrderType.GTC))
        self.order_book.process_one(OrderParams(
            OrderSide.ASK, Decimal("102.0"), 10, OrderType.GTC))
        self.assertEqual(self.order_book.midprice(), Decimal("101.0"))

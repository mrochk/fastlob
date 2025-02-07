import unittest
from decimal import Decimal
import pylob as lob

class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.ob = lob.OrderBook('A/B')

        self.orders_params = [
            lob.OrderParams(price=110,   quantity=100, side=lob.OrderSide.ASK),
            lob.OrderParams(price=110.5, quantity=100, side=lob.OrderSide.ASK),
            lob.OrderParams(price=111,   quantity=100, side=lob.OrderSide.ASK),
            lob.OrderParams(price=111.5, quantity=100, side=lob.OrderSide.ASK),
            lob.OrderParams(price=112,   quantity=100, side=lob.OrderSide.ASK),

            lob.OrderParams(price=100,   quantity=100,   side=lob.OrderSide.BID),
            lob.OrderParams(price=100.5, quantity=100,   side=lob.OrderSide.BID),
            lob.OrderParams(price=101,   quantity=100,   side=lob.OrderSide.BID),
            lob.OrderParams(price=101.5, quantity=100,   side=lob.OrderSide.BID),
            lob.OrderParams(price=102,   quantity=100,   side=lob.OrderSide.BID),
        ]

        print()

    def test_order_placement(self):
        """Test that orders are correctly placed in the book."""
        self.ob.process_many(self.orders_params)
        self.assertEqual(self.ob.nbids(), 5)
        self.assertEqual(self.ob.nasks(), 5)
        self.assertEqual(self.ob.best_bid().price(), 102)
        self.assertEqual(self.ob.best_ask().price(), 110)

    def test_market_partial_fill(self):
        """Test a market order that partially fills an existing order."""
        self.ob.process_many(self.orders_params)
        market_order = lob.OrderParams(price=110, quantity=110, side=lob.OrderSide.BID)
        self.ob.process_one(market_order)

        self.assertEqual(self.ob.best_ask().size(), 1)
        self.assertEqual(self.ob.best_ask().volume(), 90)

    def test_market_full_fill(self):
        """Test a market order that completely fills an existing order."""
        self.ob.process_many(self.orders_params)
        market_order = lob.OrderParams(price=110, quantity=100, side=lob.OrderSide.BID)
        self.ob.process_one(market_order)

        self.assertEqual(self.ob.best_ask().price(), 110.5)
        self.assertEqual(self.ob.best_ask().size(), 1)

    def test_midprice_calculation(self):
        """Test that the midprice is correctly calculated."""
        self.ob.process_many(self.orders_params)
        expected_midprice = Decimal(0.5) * (Decimal(110) + Decimal(102))
        self.assertEqual(self.ob.midprice(), expected_midprice)

    def test_spread_calculation(self):
        """Test that the spread is correctly calculated."""
        self.ob.process_many(self.orders_params)
        expected_spread = Decimal(110) - Decimal(102)
        self.assertEqual(self.ob.spread(), expected_spread)

    def test_invalid_order_price(self):
        """Test that an order with an invalid price raises an error."""
        with self.assertRaises(ValueError):
            self.ob.process_one(lob.OrderParams(price=0, quantity=100, side=lob.OrderSide.BID))

    def test_invalid_order_quantity(self):
        """Test that an order with an invalid quantity raises an error."""
        with self.assertRaises(ValueError):
            self.ob.process_one(lob.OrderParams(price=100, quantity=0, side=lob.OrderSide.BID))

    def test_best_bid_after_trade(self):
        """Ensure best bid updates correctly after a trade."""
        self.ob.process_many(self.orders_params)
        trade_order = lob.OrderParams(price=102, quantity=100, side=lob.OrderSide.ASK)
        self.ob.process_one(trade_order)

        self.assertEqual(self.ob.best_bid().price(), 101.5)
        self.assertEqual(self.ob.nbids(), 4)

    def test_best_ask_after_trade(self):
        """Ensure best ask updates correctly after a trade."""
        self.ob.process_many(self.orders_params)
        trade_order = lob.OrderParams(price=110, quantity=100, side=lob.OrderSide.BID)
        self.ob.process_one(trade_order)

        self.assertEqual(self.ob.best_ask().price(), 110.5)
        self.assertEqual(self.ob.nasks(), 4)

    
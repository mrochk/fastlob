import unittest
from decimal import Decimal
import pylob as lob

class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.ob = lob.OrderBook('A/B')

        self.orders_params = [
            lob.OrderParams(110, 100, lob.OrderSide.ASK),
            lob.OrderParams(110.5, 100, lob.OrderSide.ASK),
            lob.OrderParams(111, 100, lob.OrderSide.ASK),
            lob.OrderParams(111.5, 100, lob.OrderSide.ASK),
            lob.OrderParams(112, 100, lob.OrderSide.ASK),

            lob.OrderParams(100, 100, lob.OrderSide.BID),
            lob.OrderParams(100.5, 100, lob.OrderSide.BID),
            lob.OrderParams(101, 100, lob.OrderSide.BID),
            lob.OrderParams(101.5, 100, lob.OrderSide.BID),
            lob.OrderParams(102, 100, lob.OrderSide.BID),
        ]

        print()

    def test_order_placement(self):
        """Test that orders are correctly placed in the book."""
        self.ob.process_many(self.orders_params)
        self.assertEqual(self.ob.bids_count(), 5)
        self.assertEqual(self.ob.asks_count(), 5)
        self.assertEqual(self.ob.best_bid().price(), 102)
        self.assertEqual(self.ob.best_ask().price(), 110)

    def test_market_partial_fill(self):
        """Test a market order that partially fills an existing order."""
        self.ob.process_many(self.orders_params)
        market_order = lob.OrderParams(110, 110, lob.OrderSide.BID)
        self.ob.process_one(market_order)

        self.assertEqual(self.ob.best_ask().size(), 1)
        self.assertEqual(self.ob.best_ask().volume(), 90)

    def test_market_full_fill(self):
        """Test a market order that completely fills an existing order."""
        self.ob.process_many(self.orders_params)
        market_order = lob.OrderParams(110, 100, lob.OrderSide.BID)
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
            self.ob.process_one(lob.OrderParams(0, 100, lob.OrderSide.BID))

    def test_invalid_order_quantity(self):
        """Test that an order with an invalid quantity raises an error."""
        with self.assertRaises(ValueError):
            self.ob.process_one(lob.OrderParams(100, 0, lob.OrderSide.BID))

    def test_best_bid_after_trade(self):
        """Ensure best bid updates correctly after a trade."""
        self.ob.process_many(self.orders_params)
        trade_order = lob.OrderParams(102, 100, lob.OrderSide.ASK)
        self.ob.process_one(trade_order)

        self.assertEqual(self.ob.best_bid().price(), 101.5)
        self.assertEqual(self.ob.bids_count(), 4)

    def test_best_ask_after_trade(self):
        """Ensure best ask updates correctly after a trade."""
        self.ob.process_many(self.orders_params)
        trade_order = lob.OrderParams(110, 100, lob.OrderSide.BID)
        self.ob.process_one(trade_order)

        self.assertEqual(self.ob.best_ask().price(), 110.5)
        self.assertEqual(self.ob.asks_count(), 4)

    #def test_place_one_million(self):
        #'''Placing one million orders on both sides.'''
        #ONEMIL = int(1e6)
        #for i in range(ONEMIL):
            #if (i+1) % 1e5 == 0: print(f'order {i+1}')

            #self.ob.process_one(lob.OrderParams(
                #1000.0, 
                #1234.4567, 
                #lob.OrderSide.ASK,
            #))

            #self.ob.process_one(lob.OrderParams(
                #999.0, 
                #1234.4567, 
                #lob.OrderSide.BID,
            #))

        #self.assertEqual(self.ob.best_ask().size(), ONEMIL)
        #self.assertEqual(self.ob.best_bid().size(), ONEMIL)

        #self.assertEqual(self.ob.best_ask().volume(), self.ob.best_bid().volume())
        #self.assertEqual(
            #self.ob.best_ask().volume(),
            #lob.todecimal('1234.4567') * lob.todecimal(ONEMIL)
        #)

        #self.assertEqual(self.ob.bid_side.volume(), self.ob.ask_side.volume())

    #def test_place_100k_limits(self):
        #'''Placing 100'000 orders on both sides, at different price levels.'''

        #N = int(1e5)
        #for i in range(N):
            #if (i+1) % 1e4 == 0: print(f'order {i+1}')

            #self.ob.process_one(lob.OrderParams(
                #2*N + 1 + i, 
                #1000, 
                #lob.OrderSide.ASK,
            #))

            #self.ob.process_one(lob.OrderParams(
                #2*N - 1 - i, 
                #1000, 
                #lob.OrderSide.BID,
            #))

        #self.assertEqual(self.ob.best_ask().size(), 1)
        #self.assertEqual(self.ob.best_bid().size(), 1)

        #self.assertEqual(self.ob.bid_side.size(), N)
        #self.assertEqual(self.ob.ask_side.size(), N)

        #self.assertEqual(self.ob.best_ask().volume(), self.ob.best_bid().volume())
        #self.assertEqual(self.ob.best_ask().volume(), 1000)

        #self.assertEqual(self.ob.bid_side.volume(), self.ob.ask_side.volume())
        #self.assertEqual(self.ob.bid_side.volume(), N * 1000)
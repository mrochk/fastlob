import unittest
from decimal import Decimal
import pylob as lob

class TestOrderBook(unittest.TestCase):
    def setUp(self):
        self.ob = lob.OrderBook('A/B')
        print()

    def test_place_one_million(self):
        '''Placing one million orders on both sides.'''
        ONEMIL = int(1e6)
        for i in range(ONEMIL):
            if (i+1) % 1e5 == 0: print(f'order {i+1}')

            self.ob.process_one(lob.OrderParams(
                1000.0, 
                1234.4567, 
                lob.OrderSide.ASK,
            ))

            self.ob.process_one(lob.OrderParams(
                999.0, 
                1234.4567, 
                lob.OrderSide.BID,
            ))

        self.assertEqual(self.ob.best_ask().size(), ONEMIL)
        self.assertEqual(self.ob.best_bid().size(), ONEMIL)

        self.assertEqual(self.ob.best_ask().volume(), self.ob.best_bid().volume())
        self.assertEqual(
            self.ob.best_ask().volume(),
            lob.todecimal('1234.4567') * lob.todecimal(ONEMIL)
        )

        self.assertEqual(self.ob.bid_side.volume(), self.ob.ask_side.volume())

    def test_place_10k_limits(self):
        '''Placing 10k orders on both sides, at different price levels.'''

        N = int(1e4)
        for i in range(N):
            if (i+1) % 1e3 == 0: print(f'order {i+1}')

            self.ob.process_one(lob.OrderParams(
                2*N + 1 + i, 1000, lob.OrderSide.ASK))

            self.ob.process_one(lob.OrderParams(
                2*N - 1 - i, 1000, lob.OrderSide.BID))

        self.assertEqual(self.ob.best_ask().size(), 1)
        self.assertEqual(self.ob.best_bid().size(), 1)

        self.assertEqual(self.ob.bid_side.size(), N)
        self.assertEqual(self.ob.ask_side.size(), N)

        self.assertEqual(self.ob.best_ask().volume(), 
                         self.ob.best_bid().volume())
        self.assertEqual(self.ob.best_ask().volume(), 1000)

        self.assertEqual(self.ob.bid_side.volume(), 
                         self.ob.ask_side.volume())
        self.assertEqual(self.ob.bid_side.volume(), N * 1000)
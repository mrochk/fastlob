import unittest
from decimal import Decimal

import pylob as lob

class TestOrderBook(unittest.TestCase):
    def test_place_valid_orders(self):
        ob = lob.OrderBook()

        for _ in range(100):
            for j in range(1000):

                ob.process(
                    price=1000+j+1, 
                    quantity=1, 
                    side=lob.OrderSide.ASK,
                    type=lob.OrderType.GTC
                )

                ob.process(
                    price=1000-j-1, 
                    quantity=1, 
                    side=lob.OrderSide.BID,
                    type=lob.OrderType.GTC
                )

        self.assertEqual(ob.total_bids_lim(), ob.total_asks_lim())
        self.assertEqual(ob.total_bids_lim(), 1000)
        lim = ob.best_bid(); self.assertEqual(lim.volume, 100)

    def test_place_bids(self):
        ob = lob.OrderBook()

        ob.process(price=100, quantity=500, side=lob.OrderSide.BID)
        ob.process(price=100, quantity=500, side=lob.OrderSide.BID)
        ob.process(price=50, quantity=500, side=lob.OrderSide.BID)
        ob.process(price=50, quantity=500, side=lob.OrderSide.BID)

        self.assertEqual(ob.best_bid().volume, 1000)
        self.assertEqual(ob.best_bid().price, 100)

        self.assertEqual(ob.bids[50].volume, 1000)
        self.assertEqual(ob.bids[50].price, 50)

import unittest
from decimal import Decimal

import pylob as lob

class TestOrderBook(unittest.TestCase):
    def test_place_valid_orders(self):
        ob = lob.OrderBook()

        for i in range(100):
            for j in range(1000):
                ob.place_order(price=1000+j, quantity=1, side=lob.OrderSide.ASK)
                ob.place_order(price=1000-j, quantity=1, side=lob.OrderSide.BID)

        self.assertEqual(ob.n_bids_limits(), ob.n_asks_limits())
        self.assertEqual(ob.n_bids_limits(), 1000)
        _, limit = ob.bids.peekitem(); self.assertEqual(limit.volume, 100)

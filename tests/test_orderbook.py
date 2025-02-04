import unittest
import pylob as lob

class TestOrderBook(unittest.TestCase):
    def test_market_partial_fill(self):
        # initializing an order-book
        ob = lob.OrderBook('EUR/GBP')

        ordersp = [
            lob.OrderParams(110, 100, lob.OrderSide.ASK),
            lob.OrderParams(110.5, 100, lob.OrderSide.ASK),
            lob.OrderParams(111, 100, lob.OrderSide.ASK),
            lob.OrderParams(111.5, 100, lob.OrderSide.ASK),
            lob.OrderParams(112, 100, lob.OrderSide.ASK),

            lob.OrderParams(100,   100,   lob.OrderSide.BID),
            lob.OrderParams(100.5, 100, lob.OrderSide.BID),
            lob.OrderParams(101,   100,   lob.OrderSide.BID),
            lob.OrderParams(101.5, 100, lob.OrderSide.BID),
            lob.OrderParams(102,   100,   lob.OrderSide.BID),
        ]

        for _ in range(2): ob.process_many(ordersp)

        self.assertEqual(ob.best_ask().size(), 2)
        self.assertEqual(ob.best_ask().volume(), 200)

        marketo = lob.OrderParams(110, 110, lob.OrderSide.BID)
        ob.process_one(marketo)

        self.assertEqual(ob.best_ask().size(), 1)
        self.assertEqual(ob.best_ask().volume(), 90)
import unittest
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

            lob.OrderParams(100,   100,   lob.OrderSide.BID),
            lob.OrderParams(100.5, 100, lob.OrderSide.BID),
            lob.OrderParams(101,   100,   lob.OrderSide.BID),
            lob.OrderParams(101.5, 100, lob.OrderSide.BID),
            lob.OrderParams(102,   100,   lob.OrderSide.BID),
        ]

        print()

    def test_market_partial_fill(self):
        for _ in range(2): self.ob.process_many(self.orders_params)

        self.assertEqual(self.ob.best_ask().size(), 2)
        self.assertEqual(self.ob.best_ask().volume(), 200)

        marketo = lob.OrderParams(110, 110, lob.OrderSide.BID)
        self.ob.process_one(marketo)

        self.assertEqual(self.ob.best_ask().size(), 1)
        self.assertEqual(self.ob.best_ask().volume(), 90)

    def test_market_limit_fill(self):
        for _ in range(2): self.ob.process_many(self.orders_params)

        self.assertEqual(self.ob.best_ask().size(), 2)
        self.assertEqual(self.ob.best_ask().volume(), 200)
        self.assertEqual(self.ob.best_ask().price(), 110)

        print(self.ob)

        marketo = lob.OrderParams(110, 200, lob.OrderSide.BID)
        self.ob.process_one(marketo)

        print(self.ob)

        self.assertEqual(self.ob.best_ask().size(), 2)
        self.assertEqual(self.ob.best_ask().volume(), 200)
        self.assertEqual(self.ob.best_ask().price(), 110.5)
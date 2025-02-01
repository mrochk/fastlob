import unittest

from pylob import OrderType
from pylob.order import AskOrder, BidOrder
from pylob.limit import Limit

class TestOrder(unittest.TestCase):
    def test_pricediff(self):
        limit = Limit(price=9)

        for i in range(10, 1010):
            order = AskOrder(
                price=i,
                quantity=10,
                type=OrderType.FOK,
            )

            added = limit.add_order(order)
            self.assertFalse(added)

        self.assertEqual(limit.size(), 0)

    def test_sameorder(self):
        limit = Limit(price=9)

        order = AskOrder(
            price=9,
            quantity=100,
            type=OrderType.FOK,
        )

        added = limit.add_order(order)
        self.assertTrue(added)

        for i in range(10, 1010):
            added = limit.add_order(order)
            self.assertFalse(added)

        self.assertEqual(limit.size(), 1)

    def test_correct(self):
        limit = Limit(price=9)

        for i in range(10, 1010):
            order = AskOrder(
                price=9,
                quantity=i,
                type=OrderType.FOK,
            )

            added = limit.add_order(order)
            self.assertTrue(added)

        self.assertEqual(limit.size(), 1000)
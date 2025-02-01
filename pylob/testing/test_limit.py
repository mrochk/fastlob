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
        self.assertEqual(limit.volume, 0)

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
        self.assertEqual(limit.volume, 100)

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
        self.assertEqual(limit.volume, sum(range(10, 1010)))
    
    def test_sanity_check(self):
        limit = Limit(100)

        asko = AskOrder(100, 2, OrderType.GTC)
        bido = BidOrder(100, 2, OrderType.GTD)

        limit.add_order(asko)
        limit.add_order(bido)

        self.assertFalse(limit.sanity_check())

    def test_get_order(self):
        limit = Limit(100)

        o1 = BidOrder(100, 1, OrderType.FOK)
        o2 = BidOrder(100, 2, OrderType.FOK)
        o3 = BidOrder(100, 3, OrderType.FOK)

        id1 = o1.identifier
        id2 = o2.identifier
        id3 = o3.identifier

        limit.add_order(o1)
        limit.add_order(o2)
        limit.add_order(o3)

        self.assertEqual(limit.get_order(id1).quantity, 1)
        self.assertEqual(limit.get_order(id2).quantity, 2)
        self.assertEqual(limit.get_order(id3).quantity, 3)
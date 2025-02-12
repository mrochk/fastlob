import unittest
from decimal import Decimal
from hypothesis import given, strategies as hstrategies

from pylob.limit import Limit
from pylob.enums import OrderSide, OrderStatus
from pylob.order import OrderParams, BidOrder

class TestLimit(unittest.TestCase):
    def setUp(self):
        self.price = Decimal('100.00')
        self.side = OrderSide.BID
        self.limit = Limit(self.price, self.side)
        
    def create_test_order(self, quantity=Decimal('10.00')):
        order = BidOrder(OrderParams(self.side, self.price, quantity))
        return order

    @given(price=hstrategies.decimals(min_value='0.0', max_value='1000.00'),
           side=hstrategies.sampled_from([OrderSide.BID, OrderSide.ASK]))
    def test_init(self, price, side):
        limit = Limit(price, side)
        self.assertEqual(limit.price(), price)
        self.assertEqual(limit.side(), side)
        self.assertEqual(limit.volume(), Decimal(0))
        self.assertEqual(limit.valid_orders(), 0)

    def test_add_order(self):
        order = self.create_test_order()
        self.limit.add_order(order)
        self.assertEqual(self.limit.volume(), Decimal('10.00'))
        self.assertEqual(self.limit.valid_orders(), 1)
        self.assertTrue(self.limit.order_exists(order.id()))
        self.assertEqual(self.limit.get_order(order.id()), order)
        self.assertEqual(self.limit.get_next_order(), order)

    def test_order_exists(self):
        order = self.create_test_order()
        self.limit.add_order(order)
        self.assertTrue(self.limit.order_exists(order.id()))
        self.assertFalse(self.limit.order_exists('1234'))

    def test_get_order(self):
        order = self.create_test_order()
        self.limit.add_order(order)
        retrieved_order = self.limit.get_order(order.id())
        self.assertEqual(retrieved_order, order)

    def test_get_next_order(self):
        order1 = self.create_test_order()
        order2 = self.create_test_order()
        self.limit.add_order(order1)
        self.limit.add_order(order2)
        self.assertEqual(self.limit.get_next_order(), order1)

    def test_delete_next_order(self):
        order1 = self.create_test_order()
        order2 = self.create_test_order()
        self.limit.add_order(order1)
        self.limit.add_order(order2)
        self.limit.delete_next_order()
        self.assertEqual(self.limit.get_next_order(), order2)
        self.assertEqual(self.limit.volume(), Decimal('10.00'))
        self.assertEqual(self.limit.valid_orders(), 1)

    def test_cancel_order(self):
        order = self.create_test_order()
        self.limit.add_order(order)
        self.limit.cancel_order(order)
        self.assertEqual(order.status(), OrderStatus.CANCELED)
        self.assertEqual(self.limit.volume(), Decimal(0))
        self.assertEqual(self.limit.valid_orders(), 0)

    def test_prune_canceled_orders(self):
        order1 = self.create_test_order()
        order2 = self.create_test_order()
        self.limit.add_order(order1)
        self.limit.add_order(order2)
        order1.set_status(OrderStatus.CANCELED)
        self.limit.prune_canceled_orders()
        self.assertEqual(self.limit.get_next_order(), order2)
        self.assertEqual(self.limit.volume(), Decimal('10.00'))
        self.assertEqual(self.limit.valid_orders(), 1)

    def test_empty(self):
        self.assertTrue(self.limit.empty())
        order = self.create_test_order()
        self.limit.add_order(order)
        self.assertFalse(self.limit.empty())
        self.limit.delete_next_order()
        self.assertTrue(self.limit.empty())

    def test_repr(self):
        order = self.create_test_order()
        self.limit.add_order(order)
        expected_repr = f"{self.side.name}Limit(price={self.price}, orders=1, volume={Decimal('10.00')})"
        self.assertEqual(repr(self.limit), expected_repr)

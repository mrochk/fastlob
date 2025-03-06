import unittest
from decimal import Decimal
from hypothesis import given, strategies as st
import time

from fastlob.limit import Limit
from fastlob.enums import OrderSide, OrderStatus, OrderType
from fastlob.order import OrderParams, BidOrder, AskOrder
from fastlob.consts import MIN_VALUE, MAX_VALUE
from fastlob.utils import todecimal

valid_side = st.sampled_from(OrderSide)
valid_price = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_qty = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_otype_noGTD = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry_noGTD = st.one_of(st.none(), st.floats(min_value=time.time()+5, allow_nan=False, allow_infinity=False))

class TestLimit(unittest.TestCase):
    def setUp(self): pass

    def mkorder(self, params: OrderParams):
        return AskOrder(params) if params.side == OrderSide.ASK else BidOrder(params)

    @given(valid_price)
    def test_init(self, price):
        price = todecimal(price)
        limit = Limit(price)
        self.assertEqual(limit.price(), price)

        self.assertEqual(limit.volume(), 0)
        self.assertEqual(limit.notional(), 0)
        self.assertTrue(limit.empty())
        self.assertTrue(limit.deepempty())
        self.assertEqual(limit.valid_orders(), 0)

    @given(valid_price, valid_side, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_enqueue(self, price, side, qty, otype, expiry):
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)
        order = self.mkorder(params)

        limit.enqueue(order)

        self.assertEqual(limit.valid_orders(), 1)
        self.assertEqual(limit.next_order(), order)
        self.assertEqual(limit.volume(), order.quantity())

        limit.pop_next_order()

        self.assertTrue(limit.empty())

    @given(valid_price, valid_side, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_cancel(self, price, side, qty, otype, expiry):
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)
        order = self.mkorder(params)
        limit.enqueue(order)
        limit.cancel_order(order)

        self.assertTrue(limit.empty())
        self.assertEqual(limit.valid_orders(), 0)
        self.assertEqual(order.status(), OrderStatus.CANCELED)

    @given(valid_price, valid_side, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_cancel2_A(self, price, side, qty, otype, expiry):
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)
        order1 = self.mkorder(params)
        order2 = self.mkorder(params)

        limit.enqueue(order1)
        limit.enqueue(order2)

        self.assertEqual(limit.volume(), order1.quantity() + order2.quantity())

        limit.cancel_order(order1)

        self.assertEqual(limit.valid_orders(), 1)
        self.assertEqual(order2.status(), OrderStatus.PENDING)
        self.assertEqual(order1.status(), OrderStatus.CANCELED)
        self.assertEqual(limit.next_order(), order2)
        self.assertEqual(limit.volume(), order2.quantity())

    @given(valid_price, valid_side, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_cancel2_B(self, price, side, qty, otype, expiry):
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)
        order1 = self.mkorder(params)
        order2 = self.mkorder(params)

        limit.enqueue(order1)
        limit.enqueue(order2)

        self.assertEqual(limit.volume(), order1.quantity() + order2.quantity())

        limit.cancel_order(order2)

        self.assertEqual(limit.valid_orders(), 1)
        self.assertEqual(order1.status(), OrderStatus.PENDING)
        self.assertEqual(order2.status(), OrderStatus.CANCELED)
        self.assertEqual(limit.next_order(), order1)
        self.assertEqual(limit.volume(), order1.quantity())

    @given(valid_price, valid_side, valid_otype_noGTD, valid_expiry_noGTD)
    def test_fill_next(self, price, side, otype, expiry):
        qty = 10
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)
        order = self.mkorder(params)
        limit.enqueue(order)

        limit.fill_next(5)

        self.assertEqual(limit.next_order().quantity(), 5)
        self.assertEqual(limit.next_order().status(), OrderStatus.PARTIAL)

    @given(valid_price, valid_side, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_fill_all(self, price, side, qty, otype, expiry):
        limit = Limit(price)
        params = OrderParams(side, price, qty, otype, expiry)

        orders = list()

        for i in range(100):
            order = self.mkorder(params)
            limit.enqueue(order)
            orders.append(order)

        self.assertEqual(limit.valid_orders(), 100)
        self.assertEqual(limit.volume(), order.quantity()*100)

        limit.fill_all()

        self.assertTrue(all([o.quantity() == 0 for o in orders]))
        self.assertTrue(all([o.status() == OrderStatus.FILLED for o in orders]))
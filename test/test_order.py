import unittest
from decimal import Decimal
from hypothesis import given
import hypothesis.strategies as st
import time

from fastlob import OrderParams
from fastlob.consts import MAX_VALUE, MIN_VALUE
from fastlob.enums import OrderSide, OrderType, OrderStatus
from fastlob.utils import todecimal
from fastlob.order import Order, BidOrder, AskOrder

valid_side = st.sampled_from(OrderSide)
valid_price = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_qty = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_otype_noGTD = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry_noGTD = st.one_of(st.none(), st.floats(min_value=time.time()+5, allow_nan=False, allow_infinity=False))

class TestOrder(unittest.TestCase):
    def setUp(self): pass

    def mkorder(self, params: OrderParams):
        return AskOrder(params) if params.side == OrderSide.ASK else BidOrder(params)

    @given(valid_side, valid_price, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_init(self, side, price, qty, otype, expiry):
        params = OrderParams(side, price, qty, otype, expiry) 

        order = self.mkorder(params)

        self.assertEqual(order.side(), params.side)
        self.assertEqual(order.price(), params.price)
        self.assertEqual(order.quantity(), params.quantity)
        self.assertEqual(order.otype(), params.otype)
        self.assertEqual(order.expiry(), params.expiry)
        self.assertEqual(order.status(), OrderStatus.CREATED)

    @given(valid_side, valid_price, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_eq(self, side, price, qty, otype, expiry):
        params = OrderParams(side, price, qty, otype, expiry) 

        order1 = self.mkorder(params)
        order2 = self.mkorder(params)

        self.assertFalse(order1 == order2)

    @given(valid_side, valid_price, valid_qty, valid_otype_noGTD, valid_expiry_noGTD, valid_qty)
    def test_fill(self, side, price, qty, otype, expiry, tofill):
        params = OrderParams(side, price, qty, otype, expiry) 

        order = self.mkorder(params)
        order.fill(order.quantity() + 1)
        self.assertEqual(order.quantity(), 0)
        self.assertEqual(order.status(), OrderStatus.FILLED)

        tofill = todecimal(tofill)

        order = self.mkorder(params)
        qty = order.quantity()
        order.fill(tofill)
        if tofill >= qty: 
            self.assertEqual(0, order.quantity())
            self.assertEqual(order.status(), OrderStatus.FILLED)
        else: 
            self.assertEqual(qty - tofill, order.quantity())
            self.assertEqual(order.status(), OrderStatus.PARTIAL)
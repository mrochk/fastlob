import unittest, time
from decimal import Decimal
from hypothesis import given
import hypothesis.strategies as st

from fastlob import OrderParams
from fastlob.consts import MIN_VALUE, MAX_VALUE
from fastlob.enums import OrderSide, OrderType
from fastlob.utils import todecimal

valid_side = st.sampled_from(OrderSide)
valid_price = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_qty = st.floats(min_value=float(MIN_VALUE), max_value=float(MAX_VALUE), allow_nan=False, allow_infinity=False)
valid_otype = st.sampled_from(OrderType)
valid_otype_noGTD = st.sampled_from([OrderType.FOK, OrderType.GTC])
valid_expiry = st.one_of(st.floats(min_value=time.time()+5, allow_nan=False, allow_infinity=False))
valid_expiry_noGTD = st.one_of(st.none(), st.floats(min_value=time.time()+5, allow_nan=False, allow_infinity=False))

class TestOrderParams(unittest.TestCase):
    def setUp(self): pass

    @given(valid_side, valid_price, valid_qty, valid_otype_noGTD, valid_expiry_noGTD)
    def test_valid_init_noGTD(self, side, price, qty, otype, expiry):
        params = OrderParams(side, price, qty, otype, expiry)

        self.assertEqual(params.side, side)
        self.assertEqual(params.price, todecimal(price))
        self.assertEqual(params.quantity, todecimal(qty))
        self.assertEqual(params.otype, otype)
        if expiry is None: self.assertEqual(params.expiry, expiry)
        else: self.assertEqual(params.expiry, int(expiry))

    @given(valid_side, valid_price, valid_qty, valid_otype, valid_expiry)
    def test_valid_init(self, side, price, qty, otype, expiry):
        params = OrderParams(side, price, qty, otype, expiry)

        self.assertEqual(params.side, side)
        self.assertEqual(params.price, todecimal(price))
        self.assertEqual(params.quantity, todecimal(qty))
        self.assertEqual(params.otype, otype)
        if expiry is None: self.assertEqual(params.expiry, expiry)
        else: self.assertEqual(params.expiry, int(expiry))

    def test_invalid_side(self):
        with self.assertRaises(TypeError):
            OrderParams(None, 1, 1)

        with self.assertRaises(TypeError):
            OrderParams(42, 1, 1)

    def test_invalid_price(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, None, 1)

        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, -1, 1)

        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 0, 1)

    def test_invalid_qty(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, 1, None)

        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 1, -1)

        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 1, 0)

    def test_invalid_otype(self):
        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, 1, 1, None)

        with self.assertRaises(TypeError):
            OrderParams(OrderSide.ASK, 1, 1, 42)

    def test_invalid_expiry(self):
        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 1, 1, OrderType.GTD, None)

        with self.assertRaises(ValueError):
            OrderParams(OrderSide.ASK, 1, 1, OrderType.GTD, 12)

import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook

valid_name = st.text(max_size=1000)

class TestSide(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.FATAL)

    @given(valid_name)
    def test_init(self, name):
        lob = Orderbook(name)

        self.assertEqual(lob._name, name)

        self.assertEqual(lob.best_ask(), None)
        self.assertEqual(lob.best_bid(), None)
        self.assertEqual(lob.midprice(), None)
        self.assertEqual(lob.spread(), None)
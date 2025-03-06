import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook

valid_name = st.text(max_size=1000)
valid_loglevel = st.sampled_from([logging.INFO, logging.WARNING, logging.ERROR])

class TestSide(unittest.TestCase):
    def setUp(self): pass

    @given(valid_name, valid_loglevel)
    def test_init(self, name, loglevel):
        lob = Orderbook(name, loglevel)

        self.assertEqual(lob._NAME, name)
        self.assertEqual(lob._logger.level, loglevel)

        self.assertEqual(lob.best_ask(), None)
        self.assertEqual(lob.best_bid(), None)
        self.assertEqual(lob.midprice(), None)
        self.assertEqual(lob.spread(), None)
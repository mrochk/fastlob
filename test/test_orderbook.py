import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook

valid_name = st.text(max_size=1000)
vailid_n_snapshot = st.integers(min_value=1, max_value=100)

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

    @given(vailid_n_snapshot)
    def test_from_snapshot(self, N):

        range_bids = list(range(1, N+1))
        range_asks = list(range(N+2, 2*N+2))

        snapshot = {
            'bids': [(a, b) for a, b in zip(range_bids, range_bids)],
            'asks': [(a, b) for a, b in zip(range_asks, range_asks)],
        }

        lob = Orderbook.from_snapshot(snapshot)

        self.assertEqual(lob.n_prices(), 2*N)

        for a, b in zip(lob.best_bids(lob.n_bids()), list(reversed(snapshot['bids']))):
            self.assertTupleEqual(a[:2], b)

        for a, b in zip(lob.best_asks(lob.n_asks()), snapshot['asks']):
            self.assertTupleEqual(a[:2], b)
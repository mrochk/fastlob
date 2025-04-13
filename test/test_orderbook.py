import unittest, logging
from hypothesis import given, strategies as st

from fastlob import Orderbook

valid_name = st.text(max_size=1000)
valid_n_snapshot = st.integers(min_value=1, max_value=100)

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

    @given(valid_n_snapshot)
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

    def test_load_updates_and_step(self):
        lob = Orderbook()
        updates = [
            {"bids": [(100, 10), (99, 0)], "asks": [(101, 5), (102, 0)]},
            {"bids": [(101, 15)], "asks": [(100, 4)]},
        ]

        lob.load_updates(updates)

        # First update
        lob.step()
        self.assertEqual(lob.n_bids(), 1)
        self.assertEqual(lob.n_asks(), 1)
        self.assertEqual(lob.best_bid()[:2], (100, 10))
        self.assertEqual(lob.best_ask()[:2], (101, 5))

        # Second update
        lob.step()
        self.assertEqual(lob.n_bids(), 2)
        self.assertEqual(lob.n_asks(), 2)
        self.assertEqual(lob.best_bid()[:2], (101, 15))
        self.assertEqual(lob.best_ask()[:2], (100, 4))

    def test_step_without_load(self):
        lob = Orderbook()
        lob.step()  # Should be a no-op with no crash
        self.assertIsNone(lob.best_bid())
        self.assertIsNone(lob.best_ask())

    def test_step_after_updates_exhausted(self):
        lob = Orderbook()
        updates = [{"bids": [(99, 1)], "asks": [(101, 2)]}]
        lob.load_updates(updates)

        lob.step()  # Applies update
        self.assertEqual(lob.n_bids(), 1)
        self.assertEqual(lob.n_asks(), 1)

        lob.step()  # No-op, should not throw
        self.assertEqual(lob.n_bids(), 1)
        self.assertEqual(lob.n_asks(), 1)
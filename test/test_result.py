import unittest
from decimal import Decimal
from collections import defaultdict
from pylob.engine import PlaceResult, ExecResult


class TestEngineResults(unittest.TestCase):
    def test_place_result(self):
        result = PlaceResult(success=True, identifier=1,
                             message="Order placed successfully")
        self.assertTrue(result.success)
        self.assertEqual(result.identifier, 1)
        self.assertEqual(result.message, "Order placed successfully")

    def test_exec_result(self):
        exec_prices = defaultdict(Decimal, {Decimal("100.5"): Decimal("10")})
        result = ExecResult(
            success=True, identifier=2, message="Executed successfully",
            orders_matched=3, limits_matched=2, execution_prices=exec_prices
        )
        self.assertTrue(result.success)
        self.assertEqual(result.identifier, 2)
        self.assertEqual(result.message, "Executed successfully")
        self.assertEqual(result.orders_matched, 3)
        self.assertEqual(result.limits_matched, 2)
        self.assertEqual(
            result.execution_prices[Decimal("100.5")], Decimal("10"))

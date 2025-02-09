from abc import ABC
from decimal import Decimal
from typing import Optional
from collections import defaultdict


class EngineResult(ABC):
    success: bool
    identifier: int
    message: str

    def __init__(self, success: bool, identifier: int = 0, message: str = ""):
        self.identifier = identifier
        self.success = success
        self.message = message


class PlaceResult(EngineResult):
    def __repr__(self):
        return \
            f'PlaceResult(\n  success={self.success}\n  ' + \
            f'identifier={self.identifier}\n  message=\"{self.message}\"\n)'


class ExecResult(EngineResult):
    orders_matched: int
    limits_matched: int
    execution_prices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, success: bool, identifier: int = 0,
                 message: str = "", orders_matched: int = 0,
                 limits_matched: int = 0,
                 execution_prices: Optional[defaultdict] = defaultdict(Decimal)):

        super().__init__(success, identifier, message)
        self.orders_matched = orders_matched
        self.limits_matched = limits_matched
        self.execution_prices = execution_prices

    def __repr__(self):
        return \
            f'ExecutionResult(\n  success={self.success}\n  ' + \
            f'identifier={self.identifier}\n  message=\"{self.message}\"\n  ' + \
            f'orders_matched={self.orders_matched}\n  ' + \
            f'limits_matched={self.limits_matched}\n  ' + \
            f'prices={self.execution_prices}\n)'

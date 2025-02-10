import abc
from decimal import Decimal
from typing import Optional
from collections import defaultdict


class ExecutionResult(abc.ABC):
    _success: bool
    _order_id: str
    _message: str

    def __init__(self, success: bool, identifier: str = "",
                 message: str = ""):
        self._success = success
        self._order_id = identifier
        self._message = message

    def success(self) -> bool:
        return self._success

    def order_id(self) -> str:
        return self._order_id

    def message(self) -> str:
        return self._message


class LimitResult(ExecutionResult):
    def __init__(self, success, identifier="", message=""):
        super().__init__(success, identifier, message)

    def __repr__(self):
        return \
            f'LimitResult(success={self.success()}, ' \
            + f'order_id={self.order_id()}' \
            + f', message=\"{self.message()}\")'


class MarketResult(ExecutionResult):
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
            f'MarketResult(success={self.success()}, ' \
            + f'order_id={self.order_id()}' \
            + f', message=\"{self.message()}\", ' \
            + f'limits_matched={self.limits_matched}' \
            + f', orders_matched={self.orders_matched})'

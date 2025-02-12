import abc
from decimal import Decimal
from typing import Optional
from collections import defaultdict


class ExecutionResult(abc.ABC):
    _success: bool
    _message: str

    def __init__(self, success: bool, message: str):
        self._success = success
        self._message = message

    def success(self) -> bool:
        return self._success

    def message(self) -> str:
        return self._message


class OrderExecutionResult(ExecutionResult, abc.ABC):
    _order_id: str

    def __init__(self, success, order_id: str = '', message: str = ''):
        self._order_id = order_id
        super().__init__(success, message)

    def order_id(self) -> str:
        return self._order_id


class LimitResult(OrderExecutionResult):
    def __init__(self, success, order_id: str = '', message: str = ''):
        super().__init__(success, order_id, message)

    def __repr__(self):
        return \
            f'LimitResult(success={self.success()}, ' \
            + f'order_id={self.order_id()}' \
            + f', message=\"{self.message()}\")'


class MarketResult(OrderExecutionResult):
    orders_matched: int
    limits_matched: int
    execution_prices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, success: bool, order_id: int = 0,
                 message: str = '', orders_matched: int = 0,
                 limits_matched: int = 0,
                 execution_prices: Optional[defaultdict] = defaultdict(Decimal)):

        super().__init__(success, order_id, message)
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


class CancelResult(ExecutionResult):
    def __init__(self, success : bool, message : str = ''):
        super().__init__(success, message)

    def __repr__(self):
        return f'CancelResult(success={self.success()}, message={self.message()})'

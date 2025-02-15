import abc
from decimal import Decimal
from typing import Optional
from collections import defaultdict

class ExecutionResult(abc.ABC):
    _success: bool
    _messages: list[str]

    def __init__(self, success: bool, messages: list[str]):
        self._success = success
        self._messages = messages

    def success(self) -> bool: return self._success

    def messages(self) -> list[str]: return self._messages

    def add_message(self, message: str) -> None: self._messages.append(message)

class OrderExecutionResult(ExecutionResult, abc.ABC):
    _order_id: str

    def __init__(self, success, order_id: str = "", messages: list[str] = []):
        self._order_id = order_id
        super().__init__(success, messages)

    def order_id(self) -> str: return self._order_id

class LimitResult(OrderExecutionResult):
    def __init__(self, success, order_id: str = "", messages: list[str] = []):
        super().__init__(success, order_id, messages)

    def __repr__(self) -> str:
        return f'LimitResult(success={self.success()}, order_id={self.order_id()}, messages={self.messages()})'

class MarketResult(OrderExecutionResult):
    orders_filled: int
    limits_filled: int
    execution_prices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, success: bool, order_id: str = '', messages: list[str] = [], orders_matched: int = 0,
        limits_matched: int = 0, execution_prices: Optional[defaultdict] = defaultdict(Decimal)):

        super().__init__(success, order_id, messages)
        self.orders_filled = orders_matched
        self.limits_filled = limits_matched
        self.execution_prices = execution_prices

    def __repr__(self):
        return f'MarketResult(success={self.success()}, order_id={self.order_id()}, messages={self.messages()}, ' \
            + f'limits_matched={self.limits_filled}, orders_matched={self.orders_filled})'

class CancelResult(ExecutionResult):
    def __init__(self, success: bool, messages: list[str] = []):
        super().__init__(success, messages)

    def __repr__(self): 
        return f"CancelResult(success={self.success()}, messages={self.messages()})"

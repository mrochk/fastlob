import abc
from decimal import Decimal
from typing import Optional
from collections import defaultdict

class ExecutionResult(abc.ABC):
    _success: bool
    _messages: list[str]

    def __init__(self, success: bool, messages: Optional[list[str]]):
        self._success = success
        self._messages = messages if messages else list()

    def success(self) -> bool: return self._success

    def messages(self) -> list[str]: return self._messages

    def add_message(self, message: str) -> None: self._messages.append(message)

class OrderExecutionResult(ExecutionResult, abc.ABC):
    _order_id: str

    def __init__(self, success, order_id: str = str(), messages: Optional[list[str]] = None):
        self._order_id = order_id
        super().__init__(success, messages)

    def order_id(self) -> str: return self._order_id

class LimitResult(OrderExecutionResult):
    def __init__(self, success, order_id: str = str(), messages: Optional[list[str]] = None):
        super().__init__(success, order_id, messages)

    def __repr__(self) -> str:
        return f'LimitResult(success={self.success()}, order_id={self.order_id()}, messages={self.messages()})'

class MarketResult(OrderExecutionResult):
    _orders_matched: int
    _limits_matched: int
    _execution_prices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, success: bool, order_id: str = str(), messages: Optional[list[str]] = None, 
            orders_matched: int = 0, limits_matched: int = 0, execution_prices: Optional[defaultdict] = None):

        super().__init__(success, order_id, messages)
        self._orders_matched = orders_matched
        self._limits_matched = limits_matched
        self._execution_prices = execution_prices if execution_prices else defaultdict(Decimal)

    def orders_matched(self) -> int: return self._orders_matched

    def limits_matched(self) -> int: return self._limits_matched

    def execprices(self) -> Optional[defaultdict[Decimal, Decimal]]: return self._execution_prices

    def __repr__(self):
        return f'MarketResult(success={self.success()}, order_id={self.order_id()}, messages={self.messages()}, ' \
            + f'limits_matched={self._limits_matched}, orders_matched={self._orders_matched})'

class CancelResult(ExecutionResult):
    def __init__(self, success: bool, messages: Optional[list[str]] = None):
        super().__init__(success, messages)

    def __repr__(self): 
        return f'CancelResult(success={self.success()}, messages={self.messages()})'

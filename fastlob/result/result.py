import enum
from decimal import Decimal
from typing import Optional
from collections import defaultdict

class ResultType(enum.Enum):
    LIMIT = 0
    MARKET = 1
    CANCEL = 2

class ExecutionResult:
    _kind: ResultType
    _success: bool
    _orderid: str
    _messages: list[str]
    _orders_matched: int
    _execprices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, kind: ResultType, orderid: str):
        self._kind = kind
        self._orderid = orderid
        self._messages = list()
        self._orders_matched = 0
        self._execprices = defaultdict(Decimal) if kind == ResultType.MARKET else None

    @staticmethod
    def new_limit(orderid: str): return ExecutionResult(ResultType.LIMIT, orderid)

    @staticmethod
    def new_market(orderid: str): return ExecutionResult(ResultType.MARKET, orderid)

    @staticmethod
    def new_cancel(orderid: str): return ExecutionResult(ResultType.CANCEL, orderid)

    def kind(self) -> ResultType: return self._kind

    def success(self) -> bool: return self._success

    def orderid(self) -> str: return self._orderid

    def messages(self) -> list[str]: return self._messages.copy()

    def execprices(self) -> Optional[defaultdict[Decimal, Decimal]]: return self._execprices.copy()

    def set_success(self, success: bool): self._success = success

    def add_message(self, message: str): self._messages.append(message)

    def set_orders_matched(self, orders_matched: int): self._orders_matched = orders_matched

    def __repr__(self) -> str:
        res =  f'ExecutionResult(type={self.kind().name}, '
        res += f'success={self.success()}, orderid={self.orderid()}, messages={self.messages()})'
        return res

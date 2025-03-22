from decimal import Decimal
from typing import Optional
from collections import defaultdict

from fastlob.enums import ResultType

class ResultBuilder:
    '''The object constructed by the lob during order processing.'''

    _kind: ResultType
    _orderid: str
    _success: bool
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
    def new_limit(orderid: str): return ResultBuilder(ResultType.LIMIT, orderid)

    @staticmethod
    def new_market(orderid: str): return ResultBuilder(ResultType.MARKET, orderid)

    @staticmethod
    def new_cancel(orderid: str): return ResultBuilder(ResultType.CANCEL, orderid)

    @staticmethod
    def new_error():
        result = ResultBuilder(ResultType.ERROR, None)
        result.set_success(False)
        return result

    def success(self) -> bool: return self._success

    def set_success(self, success: bool): self._success = success

    def add_message(self, message: str): self._messages.append(message)

    def inc_execprices(self, price: Decimal, qty: Decimal): self._execprices[price] += qty

    def inc_orders_matched(self, orders_matched: int): self._orders_matched += orders_matched

    def build(self): return ExecutionResult(self)

class ExecutionResult:
    '''The object returned to the client.'''
    _kind: ResultType
    _orderid: str
    _success: bool
    _messages: list[str]
    _orders_matched: int
    _execprices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, result: ResultBuilder):
        self._kind = result._kind
        self._orderid = result._orderid
        self._success = result._success
        self._messages = result._messages
        self._orders_matched = result._orders_matched
        self._execprices = result._execprices

    def kind(self) -> ResultType: return self._kind

    def orderid(self) -> str: return self._orderid

    def success(self) -> bool: return self._success

    def messages(self) -> list[str]: return self._messages.copy()

    def n_orders_matched(self) -> int: return self._orders_matched

    def execprices(self) -> Optional[defaultdict[Decimal, Decimal]]: return self._execprices.copy()

    def __repr__(self) -> str:
        return f'ClientResult(type={self.kind().name}, success={self.success()}, ' + \
            f'orderid={self.orderid()}, messages={self.messages()})'

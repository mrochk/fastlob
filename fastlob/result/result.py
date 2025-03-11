from decimal import Decimal
from typing import Optional
from collections import defaultdict

from fastlob.enums import ResultType

class ResultBuilder:
    '''The object constructed by the lob during order processing.'''

    _KIND: ResultType
    _ORDERID: str
    _success: bool
    _messages: list[str]
    _orders_matched: int
    _execprices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, kind: ResultType, orderid: str):
        self._KIND = kind
        self._ORDERID = orderid
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

    def set_success(self, success: bool): self._success = success

    def add_message(self, message: str): self._messages.append(message)

    def set_orders_matched(self, orders_matched: int): self._orders_matched = orders_matched

    def build(self): return ExecutionResult(self)

    def __repr__(self) -> str:
        return f'ResultBuilder(type={self.kind().name}, success={self.success()}, ' + \
            f'orderid={self.orderid()}, messages={self.messages()})'

class ExecutionResult:
    '''The object returned to the client.'''
    _KIND: ResultType
    _ORDERID: str
    _success: bool
    _messages: list[str]
    _orders_matched: int
    _execprices: Optional[defaultdict[Decimal, Decimal]]

    def __init__(self, result: ResultBuilder):
        self._KIND = result._KIND
        self._ORDERID = result._ORDERID
        self._success = result._success
        self._messages = result._messages
        self._orders_matched = result._orders_matched
        self._execprices = result._execprices

    def kind(self) -> ResultType: return self._KIND

    def orderid(self) -> str: return self._ORDERID

    def success(self) -> bool: return self._success

    def messages(self) -> list[str]: return self._messages.copy()

    def n_orders_matched(self) -> int: return self._orders_matched

    def execprices(self) -> Optional[defaultdict[Decimal, Decimal]]: return self._execprices.copy()

    def __repr__(self) -> str:
        return f'ClientResult(type={self.kind().name}, success={self.success()}, ' + \
            f'orderid={self.orderid()}, messages={self.messages()})'

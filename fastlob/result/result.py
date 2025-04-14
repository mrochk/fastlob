'''The result object is returned by the LOB after the client executes an operation.'''

from decimal import Decimal
from typing import Optional
from collections import defaultdict

from fastlob.enums import ResultType

class ResultBuilder:
    '''The object constructed by the lob during execution.'''

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
    def new_limit(orderid: str):
        '''Instantiate a new limit result.'''
        return ResultBuilder(ResultType.LIMIT, orderid)

    @staticmethod
    def new_market(orderid: str):
        '''Instantiate a new market result.'''
        return ResultBuilder(ResultType.MARKET, orderid)

    @staticmethod
    def new_cancel(orderid: str):
        '''Instantiate a new cancel result.'''
        return ResultBuilder(ResultType.CANCEL, orderid)

    @staticmethod
    def new_error():
        '''Instantiate a new error result.'''
        result = ResultBuilder(ResultType.ERROR, None)
        result.set_success(False)
        return result

    def success(self) -> bool:
        '''Getter for success attribute, this attribute should be true if the operation was properly executed.'''
        return self._success

    def set_success(self, success: bool):
        '''Setter for success attribute, this attribute should be true if the operation was properly executed.'''
        self._success = success

    def add_message(self, message: str):
        '''Add an information message destined to the user.'''
        self._messages.append(message)

    def inc_execprices(self, price: Decimal, qty: Decimal):
        '''Increment the number of orders matched at a certain price.'''
        self._execprices[price] += qty

    def inc_orders_matched(self, orders_matched: int):
        '''Increment the total number of orders matched.'''
        self._orders_matched += orders_matched

    def build(self):
        '''Build the ExecutionResult object destined to the client.'''
        return ExecutionResult(self)

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

    def kind(self) -> ResultType:
        '''Getter for the result kind, one of LIMIT, CANCEL, MARKET or ERROR.'''
        return self._kind

    def orderid(self) -> str:
        '''Getter for identifier of order executed or canceled.'''
        return self._orderid

    def success(self) -> bool:
        '''Getter for success attribute, true if the operation was executed succesfully.'''
        return self._success

    def messages(self) -> list[str]:
        '''Getter for info messages.'''
        return self._messages.copy()

    def n_orders_matched(self) -> int:
        '''Getter for number of orders matched during execution.'''
        return self._orders_matched

    def execprices(self) -> Optional[defaultdict[Decimal, Decimal]]:
        '''Getter for execprices dict. This dictionary contains the quantity matched at each price level.'''
        return self._execprices.copy()

    def __repr__(self) -> str:
        return f'ExecutionResult(type={self.kind().name}, success={self.success()}, ' + \
            f'orderid={self.orderid()}, messages={self.messages()})'

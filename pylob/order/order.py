import uuid
from abc import ABC
from enum import Enum
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass

from pylob.enums import OrderSide, OrderType, OrderStatus
from .params import OrderParams


@dataclass
class Order(ABC):
    '''
    Base abstract class for orders in the order-book. 
    Extended by `BidOrder` and `AskOrder`.
    '''
    _id: int
    _price: Decimal
    _quantity: Decimal
    _type: OrderType
    _side: OrderSide
    _expiry: Optional[float]
    _status: OrderStatus

    def __init__(self, params: OrderParams):
        self._price = params.price
        self._quantity = params.quantity
        self._type = params.type
        self._expiry = params.expiry

        self._id = uuid.uuid4().int
        self._status = OrderStatus.CREATED

    def status(self) -> OrderStatus:
        '''Getter for order status.

        Returns:
            OrderStatus: The order status.
        '''
        return self._status

    def set_status(self, status: OrderStatus):
        self._status = status

    def id(self) -> int:
        '''Getter for order identifier.

        Returns:
            int: The unique order identifier.
        '''
        return self._id

    def price(self) -> Decimal:
        '''Getter for order price.

        Returns:
            Decimal: The price at which the order should be matched.
        '''
        return self._price

    def quantity(self) -> Decimal:
        '''Getter for order quantity.

        Returns:
            Decimal: The quantity of asset the order carries.
        '''
        return self._quantity

    def type(self) -> OrderType:
        '''Getter for order type

        Returns:
            OrderType: The type of the order.
        '''
        return self._type

    def expiry(self) -> Optional[float]:
        '''Getter for the expiration date of the order. Only relevant in the 
        case of a GTD order, otherwise may be set to `None`.

        Returns:
            Optional[float]: The expiration timestamp of the order.
        '''
        return self._expiry

    def side(self) -> OrderSide:
        '''Getter for the order side.

        Returns:
            OrderSide: The side of the order.
        '''
        return self._side

    def fill(self, quantity: Decimal):
        '''Decrease the quantity of the order by some numerical value.

        Args:
            quantity (num): The amount to subtract to the order quantity.
        '''
        self._quantity -= quantity

        if self.quantity() == 0:
            self.set_status(OrderStatus.FILLED)
            return

        self.set_status(OrderStatus.PARTIAL)

    def __eq__(self, other):
        '''Two orders are equal if they're (unique) ids are equal.'''
        return self.id() == other.id()

    def __repr__(self) -> str:
        fst, lst = str(self._id)[0], str(self._id)[-1]
        return f'Order(id={fst}..{lst}, s={self.status()}, p={self.price()},' +\
            f' q={self.quantity()}, t={self.type()})'


@dataclass
class BidOrder(Order):
    '''
    A bid (buy) order.
    '''

    def __init__(self, params: OrderParams):
        super().__init__(params)
        self._side = OrderSide.BID

    def __repr__(self) -> str: return 'Bid' + super().__repr__()


@dataclass
class AskOrder(Order):
    '''
    An ask (sell) order.
    '''

    def __init__(self, params: OrderParams):
        super().__init__(params)
        self._side = OrderSide.ASK

    def __repr__(self) -> str: return 'Ask' + super().__repr__()

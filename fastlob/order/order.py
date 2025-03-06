import abc, secrets
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass

from fastlob.enums import OrderSide, OrderType, OrderStatus
from fastlob.consts import ORDERS_ID_SIZE
from .params import OrderParams

@dataclass
class Order(abc.ABC):
    '''Base abstract class for orders in the order-book. Extended by `BidOrder` and `AskOrder`.'''

    _id: str
    _side: OrderSide
    _price: Decimal
    _quantity: Decimal
    _otype: OrderType
    _expiry: Optional[float]
    _status: OrderStatus

    def __init__(self, params: OrderParams):
        self._id       = secrets.token_urlsafe(nbytes=ORDERS_ID_SIZE)
        self._price    = params.price
        self._quantity = params.quantity
        self._otype    = params.otype
        self._expiry   = params.expiry
        self._status   = OrderStatus.CREATED

    def id(self) -> str:
        '''Getter for order identifier.'''
        return self._id

    def side(self) -> OrderSide:
        '''Getter for order side.'''
        return self._side

    def price(self) -> Decimal:
        '''Getter for order price.'''
        return self._price

    def quantity(self) -> Decimal:
        '''Getter for order quantity.'''
        return self._quantity

    def otype(self) -> OrderType:
        '''Getter for order type.'''
        return self._otype

    def expiry(self) -> Optional[float]:
        '''Getter for the expiration date of the order. Only relevant in the case of a GTD order.'''
        return self._expiry

    def status(self) -> OrderStatus:
        '''Getter for order status.'''
        return self._status

    def set_status(self, status: OrderStatus):
        '''Set the order status.'''
        self._status = status

    def fill(self, quantity: Decimal):
        '''Decrease the quantity of the order by some numerical value. If `quantity` is greater than the order qty, 
        we set it to 0.
        '''
        self._quantity -= min(quantity, self._quantity)
        if self.quantity() == 0: self.set_status(OrderStatus.FILLED); return
        self.set_status(OrderStatus.PARTIAL)

    def valid(self) -> bool:
        '''True if order is valid (can be matched).'''
        return self.status() in OrderStatus.valid_states()

    def __eq__(self, other):
        '''Two orders are equal if they're (unique) ids are equal.'''
        return self.id() == other.id()

    def __repr__(self) -> str:
        return f'{self._side.name}Order(id={self.id()}, s={self.status()}, p={self.price()}, ' + \
            'q={self.quantity()}, t={self.otype()})'

@dataclass
class BidOrder(Order):
    '''A bid (buy) order.'''

    def __init__(self, params: OrderParams):
        super().__init__(params)
        self._side = OrderSide.BID

@dataclass
class AskOrder(Order):
    '''An ask (sell) order.'''

    def __init__(self, params: OrderParams):
        super().__init__(params)
        self._side = OrderSide.ASK
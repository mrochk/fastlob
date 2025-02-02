import uuid
from abc import ABC
from enum import Enum
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass

from pylob import todecimal
from pylob.consts import num

class OrderSide(Enum):
    BID = False
    ASK = True

class OrderType(Enum):
    '''The type of the order, can be FOK, GTC or GTD.'''
    FOK = 1, 
    '''A fill or kill (FOK) order is a conditional order requiring the 
    transaction to be executed immediately and to its full amount at a stated 
    price. If any of the conditions are broken, then the order must be 
    automatically canceled (kill) right away.'''
    GTC = 2, 
    '''A Good-Til-Cancelled (GTC) order is an order to buy or sell a stock that 
    lasts until the order is completed or canceled.
    '''
    GTD = 3, 
    '''A 'Good-Til-Day' order is a type of order that is active until its 
    specified date (UTC seconds timestamp), unless it has already been 
    fulfilled or cancelled. There is a security threshold of one minute: 
    If the order needs to expire in 30 seconds the correct expiration value is: 
    now + 1 minute + 30 seconds
    '''

@dataclass
class Order(ABC):
    '''
    Base class for orders in the order-book.
    '''
    _id       : int
    _price    : Decimal
    _quantity : Decimal
    _type     : OrderType
    _side     : OrderSide
    _expiry   : float

    def __init__(self, price : num, quantity : num, type : OrderType,
                 expiry : Optional[float] = None):
        '''
        Args:
            `price` (num): The price at which the order must sit.
            `quantity` (num): The quantity to buy/sell.
            `type` (OrderType): The type of order (see pylob.order.OrderType).
            `expiry` (float): The timestamp after which the order becomes 
            invalid, only relevant for GTD orders, otherwise can be None.
        '''
        if price <= 0 or quantity <= 0: raise ValueError()

        self._id       = uuid.uuid4().int
        self._price    = todecimal(price)
        self._quantity = todecimal(quantity)
        self._type     = type
        self._expiry   = expiry

    # getters
    def id(self)       -> int:             return self._id
    def price(self)    -> Decimal:         return self._price
    def quantity(self) -> Decimal:         return self._quantity
    def type(self)     -> OrderType:       return self._type
    def expiry(self)   -> Optional[float]: return self._expiry
    def side(self)     -> OrderSide:       return self._side

    def partial_fill(self, quantity : num):
        quantity = todecimal(quantity)
        if self.quantity() < quantity:  
            raise ValueError() # raise if negative (can be 0)
        self._quantity -= quantity

    def __eq__(self, other): 
        return self.id() == other.id()

    def __repr__(self) -> str:
        fst, lst = str(self._id)[0], str(self._id)[-1]
        return f'Order(id={fst}..{lst}, p={self._price}, ' + \
            f'q={self._quantity}, t={self._type})'

@dataclass
class BidOrder(Order):
    '''
    A bid (buy) order.
    '''
    def __init__(self, price : num, quantity : num, type : OrderType,
                 expiry : Optional[float] = None):
        super().__init__(price, quantity, type, expiry)
        self._side = OrderSide.BID

    def __repr__(self) -> str: return 'Bid' + super().__repr__()

@dataclass
class AskOrder(Order):
    '''
    An ask (sell) order.
    '''
    def __init__(self, price : num, quantity : num, type : OrderType,
                 expiry : Optional[float] = None):
        super().__init__(price, quantity, type, expiry)
        self._side = OrderSide.ASK

    def __repr__(self) -> str: return 'Ask' + super().__repr__()

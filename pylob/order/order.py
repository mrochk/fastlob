import uuid
from abc import ABC
from enum import Enum
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass

from pylob import todecimal
from pylob.consts import num

class OrderStatus(Enum):
    '''The side of an order/limit, can be BID or ASK.'''
    CREATED  = 1
    IN_LINE  = 2
    MATCHED  = 3
    CANCELED = 4
    PARTIAL  = 5

class OrderSide(Enum):
    '''The side of an order/limit, can be BID or ASK.'''
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
    Base abstract class for orders in the order-book.
    Extended by BidOrder and AskOrder.
    '''
    _id       : int
    _price    : Decimal
    _quantity : Decimal
    _type     : OrderType
    _side     : OrderSide
    _expiry   : Optional[float]
    _status   : OrderStatus

    def __init__(self, price : num, quantity : num, type : OrderType,
                 expiry : Optional[float] = None):
        '''
        Args:
            price (num): The price at which the order must sit.
            quantity (num): The quantity to buy/sell.
            type (OrderType): The type of order (see pylob.order.OrderType).
            expiry (float): The timestamp after which the order becomes 
            invalid, only relevant for GTD orders, otherwise can be None.
        '''
        self._price    = todecimal(price)
        self._quantity = todecimal(quantity)

        if self._price <= 0 or self._quantity <= 0: 
            raise ValueError(
                f'price ({self._price}) or qty ({self._quantity}) negative'
            )

        self._id       = uuid.uuid4().int
        self._type     = type
        self._expiry   = expiry
        self._status   = OrderStatus.CREATED

    def status(self) -> int:
        '''Getter for order status.

        Returns:
            OrderStatus: The order status.
        '''
        return self._status

    def set_status(self, status : OrderStatus):
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

    def partial_fill(self, quantity : num):
        '''Decrease the quantity of the order by some numerical value.

        Args:
            quantity (num): The amount to subtract to the order quantity.

        Raises:
            ValueError: If the quantity to subtract is negative. 
            ValueError: If the order quantity is lower than the amount to 
            subtract (would not be a partial fill in that case).
        '''
        quantity = todecimal(quantity)

        if quantity < 0: 
            raise ValueError(f'can not remove negative amount ({quantity})')

        if self.quantity() < quantity:  
            raise ValueError(f'order quantity {self.quantity()} lower ' + \
                    'than amount to subtract ({quantity})')

        self._quantity -= quantity

    def __eq__(self, other): 
        '''Two orders are equal if they're (unique) ids are equal.'''
        return self.id() == other.id()

    def __repr__(self) -> str:
        fst, lst = str(self._id)[0], str(self._id)[-1]
        return f'Order(id={fst}..{lst}, s={self.status()}, p={self.price()},'+\
            f' q={self.quantity()}, t={self.type()})'

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

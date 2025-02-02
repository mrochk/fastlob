from enum import Enum
from abc import ABC, abstractmethod
from decimal import Decimal
import uuid

from pylob import todecimal
from pylob.consts import num

class OrderSide(Enum):
    BID = False
    ASK = True

class OrderType(Enum):
    '''
    FOK = Fill Or Kill       \n
    GTC = Good Till Canceled \n
    GTD = Good Till Day
    '''
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

class Order(ABC):
    identifier : int
    price      : Decimal
    quantity   : Decimal
    type       : OrderType
    side       : OrderSide

    def __init__(self, price : num, quantity : num, type : OrderType):
        self.identifier = uuid.uuid4().int
        self.price      = todecimal(price)
        self.quantity   = todecimal(quantity)
        self.type       = type

    def __repr__(self) -> str:
        fst, lst = str(self.identifier)[0], str(self.identifier)[-1]
        return f'Order(id={fst}..{lst}, p={self.price}, ' + \
            f'q={self.quantity}, t={self.type})'

class BidOrder(Order):
    def __init__(self, price : num, quantity : num, type : OrderType):
        super().__init__(price, quantity, type)
        self.side = OrderSide.BID

    def __repr__(self) -> str: return 'Bid' + super().__repr__()

class AskOrder(Order):
    def __init__(self, price : num, quantity : num, type : OrderType):
        super().__init__(price, quantity, type)
        self.side = OrderSide.ASK

    def __repr__(self) -> str: return 'Ask' + super().__repr__()

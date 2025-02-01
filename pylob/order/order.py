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
    FOK = 1
    GTC = 2
    GTD = 3

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

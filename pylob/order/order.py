from enum import Enum
from abc import ABC, abstractmethod
from pylob import todecimal
from pylob.utils import get_uuid
from decimal import Decimal

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

    def __init__(self, price : (float | int | Decimal), 
                 quantity : (float | int | Decimal), type : OrderType):

        self.identifier = get_uuid()
        self.price      = todecimal(price)
        self.quantity   = todecimal(quantity)
        self.type       = type

    def __repr__(self) -> str:
        return f'Order(id={self.identifier}, p={self.price},' + \
            f'q={self.quantity}, t={self.type})'

    @abstractmethod
    def is_bid(self) -> bool: pass

class BidOrder(Order):
    def __init__(self, price : (float | int | Decimal), 
                 quantity : (float | int | Decimal), type : OrderType):

        super().__init__(price, quantity, type)

    def is_bid(self) -> bool: return True

    def __repr__(self) -> str:
        return 'Bid' + super().__repr__()

class AskOrder(Order):
    def __init__(self, price : (float | int | Decimal), 
                 quantity : (float | int | Decimal), type : OrderType):

        super().__init__(price, quantity, type)

    def is_bid(self) -> bool: return False

    def __repr__(self) -> str:
        return 'Ask' + super().__repr__()

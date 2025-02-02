from abc import ABC
from decimal import Decimal
from sortedcollections import SortedDict

from pylob import OrderSide
from pylob.order import Order
from pylob.consts import num
from pylob.limit import Limit

class Side(ABC):
    '''
    A side is a collection of limits whose ordering depends if it is 
    a BidSide or AskSide.
    '''
    _limits : SortedDict
    _side   : OrderSide

    def side(self) -> OrderSide: return self._side

    def size(self) -> int: return len(self._limits.keys())

    def best(self) -> Limit: 
        _, lim = self._limits.peekitem(0); return lim

    def volume(self) -> Decimal: 
        return Decimal(sum([lim.volume() for lim in self._limits.values()]))

    def prices(self) -> set: return set(self._limits.keys())

    def limit_exists(self, price : num) -> None: 
        return price in self.prices()

    def add_limit(self, price : num) -> None: 
        if self.limit_exists(price): 
            raise ValueError(f'price {price} already in side')
        self._limits[price] = Limit(price, self.side())

    def add_order(self, order : Order): 
        if not self.limit_exists(order.price()): 
            raise ValueError(f'order price {order.price()} not in side')
        lim : Limit = self._limits[order._price]
        return lim.add_order(order)

    def remove_limit(self, price : num) -> None:
        if not self.limit_exists(price): 
            raise ValueError(f'price {price} not in side')
        del self._limits[price]

class BidSide(Side):
    def __init__(self):
        self._side   = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

class AskSide(Side):
    def __init__(self):
        self._side   = OrderSide.ASK
        self._limits = SortedDict()
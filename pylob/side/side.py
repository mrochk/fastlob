from sortedcollections import SortedDict
from abc import ABC, abstractmethod
from decimal import Decimal

from pylob import OrderSide
from pylob.order import Order
from pylob.consts import num
from pylob.limit import Limit

class Side(ABC):
    _limits : SortedDict
    _side   : OrderSide

    def best(self) -> Limit:
        _, lim = self._limits.peekitem(0)
        return lim

    def volume(self) -> Decimal: 
        return sum([lim.volume() for lim in self._limits.values()])

    def size(self) -> int: return len(self._limits.keys())

    def prices(self) -> set: return set(self._limits.keys())

    def limit_exist(self, price : num) -> None: 
        return price in self.prices()

    def add_limit(self, price : num) -> None: 
        assert price not in self.prices()
        self._limits[price] = Limit(price, self.side())

    def add_order(self, order : Order) -> bool: 
        assert order._price in self.prices()
        lim : Limit = self._limits[order._price]
        return lim.add_order(order)

    def remove_limit(self, price) -> None:
        assert price in self.prices
        del self._limits[price]

    def side(self) -> OrderSide: return self._side

class BidSide(Side):
    def __init__(self):
        self._side   = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

class AskSide(Side):
    def __init__(self):
        self._side   = OrderSide.ASK
        self._limits = SortedDict()
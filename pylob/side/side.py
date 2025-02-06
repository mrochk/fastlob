import io
from abc import ABC
from decimal import Decimal
from sortedcollections import SortedDict

from pylob.enums import OrderSide
from pylob.order import Order
from pylob.consts import num
from pylob.limit import Limit

class Side(ABC):
    '''
    A side is a collection of limits, whose ordering by price depends if it is 
    a BidSide or AskSide.
    '''
    _limits : SortedDict[Decimal, Limit]
    _orders : dict[int, Order]
    _side   : OrderSide
    _volume : Decimal

    def __init__(self):
        self._orders = dict()
        self._volume = Decimal(0)

    def size(self): return len(self._limits)

    def side(self) -> OrderSide:
        return self._side

    def add_limit(self, price : Decimal):
        self._limits[price] = Limit(price, self.side())

    def price_exists(self, price : Decimal) -> bool:
        return price in self._limits.keys()

    def get_limit(self, price : Decimal) -> Limit:
        return self._limits[price]

    def place_order(self, order : Order):
        self._limits[order.price()] = order
        self._orders[order.id()]    = order
        self._volume               += order.quantity()

    def get_order(self, order_id : int):
        return self._orders[order_id]

    def remove_order(self, order_id : int):
        order = self.get_order(order_id)
        self._volume -= order.quantity()
        del self._orders[order_id]

        if self.get_limit(order.price()).empty():
            del self._limits[order.price()]

    def best(self) -> Limit:
        return self._limits.peekitem(0)[1]

    def empty(self) -> bool:
        return self.size() == 0

class BidSide(Side):
    '''The bid side, where the best price level is the highest. '''
    def __init__(self):
        super().__init__()
        self._side   = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

    def __repr__(self):
        mkline = lambda lim: ' - ' + str(lim) + '\n'
        buffer = io.StringIO()
        i = 0
        for bidlim in self._limits.values(): 
            if i > 10: 
                if i < self.size(): 
                    buffer.write(f'...({self.size() - 10} more bids)\n')
                break
            i += 1
            buffer.write(mkline(bidlim))
        return buffer.getvalue()

class AskSide(Side):
    '''The bid side, where the best price level is the lowest. '''
    def __init__(self):
        super().__init__()
        self._side   = OrderSide.ASK
        self._limits = SortedDict()

    def __repr__(self):
        mkline = lambda lim: ' - ' + str(lim) + '\n'
        buffer = io.StringIO()
        ten_asks = list()
        i = 0
        for asklim in self._limits.values():
            if i > 10: break
            i += 1
            ten_asks.append(asklim)

        if self.size() > 10: buffer.write(f'...({self.size() - 10} more asks)\n')

        for asklim in reversed(ten_asks):
            length = buffer.write(mkline(asklim)) - 2

        return buffer.getvalue()
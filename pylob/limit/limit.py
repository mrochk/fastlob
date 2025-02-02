from decimal import Decimal
from collections import deque
from typing import Optional

from pylob import todecimal, OrderSide
from pylob.order import Order
from pylob.consts import num

class Limit:
    '''
    A limit is a collection of orders.
    '''
    _price    : Decimal
    _side     : OrderSide
    _volume   : Decimal
    _orderq   : deque[Order]
    _ordermap : dict[int, Order]

    def __init__(self, price : num, side : OrderSide):
        self._price    = todecimal(price)
        self._side     = side
        self._volume   = Decimal(0)
        self._orderq   = deque()
        self._ordermap = dict()

    def price(self) -> Decimal: return self._price

    def volume(self) -> Decimal: return self._volume

    def side(self) -> OrderSide: return self._side

    def size(self) -> int: return len(self._orderq)

    def add_order(self, order : Order):
        assert order.quantity() > 0
        assert self.price() == order.price()
        assert not self.order_exists(order.id())
        assert order.side() == self.side()

        # add order
        self._ordermap[order.id()] = order
        self._orderq.append(order)

        # add volume
        self._volume = self.volume() + order.quantity()

        self.sanity_check()

    def order_exists(self, identifier : int) -> bool:
        return identifier in self._ordermap

    def get_order(self, identifier : int) -> Order:
        assert self.order_exists(identifier)
        return self._ordermap[identifier]

    def next_order(self) -> Order: 
        assert self.size() > 0
        return self._orderq[0]

    def pop_next_order(self) -> None: 
        assert self.size() > 0
        order = self._orderq.popleft()
        self._ordermap.pop(order.id())

        self.sanity_check()

    def display_orders(self) -> None: print(self._orderq)

    def sanity_check(self):
        '''
        Check if price correct for all orders,
        no duplicates and all of same side.
        '''
        assert all([o.side() == self.side() for o in self._orderq])
        assert all([o.price() == self.price() for o in self._orderq])
        assert len(self._ordermap.keys()) == len(self._orderq)
        assert self.volume() == sum([o.quantity() for o in self._orderq])

    def __repr__(self) -> str:
        p, s, v = self.price(), self.size(), self.volume()
        return f'Limit(price={p}, size={s}, volume={v})'
from decimal import Decimal
from collections import deque
from typing import Optional

from pylob import todecimal, OrderSide
from pylob.order import Order
from pylob.consts import num

class Limit:
    '''
    A limit is a collection of orders sitting at a certain price.
    '''
    _price    : Decimal
    _side     : OrderSide
    _volume   : Decimal
    _orderq   : deque[Order]
    _ordermap : dict[int, Order]

    def __init__(self, price : num, side : OrderSide):
        '''
        Args:
            price (num): The price at which the limit will sit.
            side (OrderSide): The side of the limit.
        '''
        self._price    = todecimal(price)
        self._side     = side
        self._volume   = Decimal(0)
        self._orderq   = deque()
        self._ordermap = dict()

    # getters
    def price(self)  -> Decimal:   return self._price
    def volume(self) -> Decimal:   return self._volume
    def side(self)   -> OrderSide: return self._side
    def size(self)   -> int:       return len(self._orderq)

    def add_order(self, order : Order):
        '''
        Add an order to the limit.
        '''
        self.add_order_sanity_check(order)

        # add order
        self._ordermap[order.id()] = order
        self._orderq.append(order)

        # add volume
        self._volume = self.volume() + order.quantity()

        self.limit_sanity_check()

    def order_exists(self, identifier : int) -> bool:
        '''
        True if order is in limit false otherwise.
        '''
        return identifier in self._ordermap

    def get_order(self, identifier : int) -> Order:
        '''
        Get order by its id.
        '''
        if not self.order_exists(identifier):
            raise ValueError(f'order with id ({identifier}) not in limit')
        return self._ordermap[identifier]

    def next_order(self) -> Order: 
        '''
        Returns the next order to be executed.
        '''
        if self.size() == 0: raise ValueError('order queue is empty')
        return self._orderq[0]

    def pop_next_order(self) -> Order: 
        '''
        Pop and return the next order to be executed.
        '''
        if self.size() == 0: raise ValueError('order queue is empty')
        order = self._orderq.popleft()
        self._ordermap.pop(order.id())
        self._volume -= order.quantity()

        self.limit_sanity_check()

        return order

    def display_orders(self) -> None: print(self._orderq)

    def add_order_sanity_check(self, order):
        '''
        Raise exception if order can't be added to limit.
        '''
        if not self.price() == order.price(): 
            raise ValueError(f'order price ({order.price()}) and limit ' + \
                    f'price ({self.price()}) do not match')

        if self.order_exists(order.id()): 
            raise ValueError(f'order with id {order.id()} already in limit')

        if not order.side() == self.side():
            raise ValueError(f'order side {order.side()} does not match' + \
                    f'limit side {self.side()}')

    def limit_sanity_check(self):
        '''
        Check if price correct for all orders, no duplicates and all of 
        same side.
        NOTE: This check is expensive and should only be used during 
        development, but removed in production.
        '''
        assert all([o.side() == self.side() for o in self._orderq])
        assert all([o.price() == self.price() for o in self._orderq])
        assert len(self._ordermap.keys()) == len(self._orderq)
        assert self.volume() == sum([o.quantity() for o in self._orderq])

    def __repr__(self) -> str:
        p, s, v = self.price(), self.size(), self.volume()
        return f'Limit(price={p}, size={s}, volume={v})'
from decimal import Decimal
from collections import deque
from typing import Optional

from pylob import todecimal, OrderSide
from pylob.order import Order, OrderStatus
from pylob.consts import num

class Limit:
    '''
    A limit is a collection of limit orders sitting at a certain price.
    '''
    _price    : Decimal
    _side     : OrderSide
    _volume   : Decimal
    _orderq   : deque[Order]
    _ordermap : dict[int, Order]
    _done     : dict[int, Order]

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
        self._done     = dict()

    def match_all(self):
        for order in self._orderq:
            order.set_status(OrderStatus.MATCHED)
            order.fill(order.quantity())
            self._done[order.id()] = order

        self._orderq.clear()
        self._ordermap.clear()
        self._volume = Decimal(0)

    def partial_fill(self, order_id : int, quantity : Decimal):
        self._ordermap[order_id].fill(quantity)
        self._volume -= quantity

    def price(self) -> Decimal: 
        '''Getter for limit price.

        Returns:
            Decimal: The price at which the limit is sitting.
        '''
        return self._price

    def volume(self) -> Decimal: 
        '''Getter for limit volume (sum of orders quantity).

        Returns:
            Decimal: The volume of the limit.
        '''
        return self._volume

    def side(self) -> OrderSide: 
        '''Getter for limit side (Bid or Ask).

        Returns:
            OrderSide: The side of the limit.
        '''
        return self._side

    def size(self) -> int:
        '''Getter for limit size (number of orders).

        Returns:
            int: The size of the limit.
        '''
        return len(self._orderq)

    def empty(self) -> bool:
        return self.size() == 0

    def add_order(self, order : Order):
        '''Add (enqueue) an order to the limit.

        Args:
            order (Order): The order to add.
        '''
        
        self.add_order_sanity_check(order)

        # add order
        self._ordermap[order.id()] = order
        self._orderq.append(order)

        order.set_status(OrderStatus.IN_LINE)

        # add volume
        self._volume += order.quantity()

    def order_exists(self, identifier : int) -> bool:
        '''Returns true if an order with the given id is in the limit.

        Args:
            identifier (int): The id of the order to look for.

        Returns:
            bool: True if order is present in limit false otherwise.
        '''
        return identifier in self._ordermap

    def get_order(self, identifier : int) -> Order:
        '''Returns the order with the corresponding id.

        Args:
            identifier (int): The id of the order.

        Raises:
            ValueError: If no such order is in the limit.

        Returns:
            Order: The order having such identifier.
        '''
        if not self.order_exists(identifier):
            raise ValueError(f'order with id ({identifier}) not in limit')

        return self._ordermap[identifier]

    def next_order(self) -> Order: 
        '''Returns the next order to be matched by an incoming market order.

        Raises:
            ValueError: If the limit is empty.

        Returns:
            Order: The next order to be executed.
        '''
        if self.empty(): raise ValueError('order queue is empty')

        return self._orderq[0]

    def pop_next_order(self) -> Order: 
        '''Delete from the queue and return the next order to be executed.

        Raises:
            ValueError: If the limit is empty.

        Returns:
            Order: The next order to be executed.
        '''
        if self.empty(): raise ValueError('order queue is empty')

        order = self._orderq.popleft()
        del self._ordermap[order.id()]
        self._volume -= order.quantity()

        self._done[order.id()] = order

        return order

    def display_orders(self) -> None: 
        '''Print the order-queue.'''
        print(self._orderq)

    def add_order_sanity_check(self, order) -> None:
        '''Raise exception if order can't be added to limit.

        Raises:
            ValueError: If the order price is not the same as the limit price.
            ValueError: If the order is already in the limit.
            ValueError: If the side of the order and the limit are different.
        '''
        if not self.price() == order.price(): 
            raise ValueError(f'order price ({order.price()}) and limit ' + \
                    f'price ({self.price()}) do not match')

        if not order.side() == self.side():
            raise ValueError(f'order side {order.side()} does not match' + \
                    f'limit side {self.side()}')

        #if self.order_exists(order.id()): 
            #raise ValueError(f'order with id {order.id()} already in limit')

    def limit_sanity_check(self) -> None:
        '''
        Check if price correct for all orders, 
        no duplicates and all of same side.
        NOTE: This check is expensive and should only be 
        used during development, but removed in production.
        '''
        assert all([o.side() == self.side() for o in self._orderq])
        assert all([o.price() == self.price() for o in self._orderq])
        assert len(self._ordermap.keys()) == len(self._orderq)
        assert self.volume() == sum([o.quantity() for o in self._orderq])

    def __repr__(self) -> str:
        p, s, v = self.price(), self.size(), self.volume()
        return f'{self.side().name}Limit(price={p}, size={s}, volume={v})'
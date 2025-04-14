'''A limit is a collection of limit orders sitting at a certain price.'''

from decimal import Decimal
from collections import deque

from fastlob.order import Order
from fastlob.enums import OrderStatus
from fastlob.utils import zero

class Limit:
    '''A limit is a collection of limit orders sitting at a certain price.'''

    _price: Decimal
    _volume: Decimal
    _valid_orders: int
    _orderqueue: deque[Order]
    _fakeorder: Order

    def __init__(self, price: Decimal):
        '''
        Args:
            price (num): The price at which the limit will sit.
        '''
        self._price        = price
        self._volume       = zero()
        self._valid_orders = 0
        self._orderqueue   = deque()
        self._fakeorder    = None

    def price(self) -> Decimal:
        '''Getter for limit price.'''
        return self._price

    def volume(self) -> Decimal:
        '''Getter for limit volume (sum of orders quantity).'''
        return self._volume

    def notional(self) -> Decimal:
        '''Notional = limit price * limit volume.'''
        return self.price() * self.volume()

    def valid_orders(self) -> int:
        '''Getter for limit size (number of orders).'''
        return self._valid_orders

    def empty(self) -> bool:
        '''Check if limit contains zero **valid** orders, not if the limit queue is empty.'''
        return self.valid_orders() == 0

    def deepempty(self):
        '''Check if limit contains zero orders.'''
        return len(self._orderqueue) == 0

    def next_order(self) -> Order:
        '''Returns the next order to be matched by an incoming market order.'''
        self._prune_canceled()
        return self._orderqueue[0]

    def enqueue(self, order: Order):
        '''Add (enqueue) an order to the limit order queue.'''
        self._orderqueue.append(order)
        order.set_status(OrderStatus.PENDING)
        self._volume += order.quantity()
        self._valid_orders += 1

    def fill_next(self, quantity: Decimal):
        '''**Partially** fill the next order in the queue. Filling it entirely would lead to problems, to only use in 
        last stage of order execution (`engine._partial_fill_order`).
        '''
        order = self.next_order()
        order.fill(quantity)
        self._volume -= quantity

    def fill_all(self):
        '''Fill all orders in limit.'''
        while self.valid_orders() > 0:
            order = self.next_order()
            order.fill(order.quantity())
            self.pop_next_order()

    def pop_next_order(self) -> None:
        '''Pop from the queue the next order to be executed. Does not return it, only removes it.'''
        self._prune_canceled()
        order = self._orderqueue.popleft()
        self._valid_orders -= 1
        self._volume -= order.quantity()

    def cancel_order(self, order: Order) -> None:
        '''Cancel an order.'''
        self._volume -= order.quantity()
        self._valid_orders -= 1
        order.set_status(OrderStatus.CANCELED)

    def _prune_canceled(self) -> None:
        '''Pop the next order while it is a canceled one.'''
        while not self.deepempty() and self._orderqueue[0].status() == OrderStatus.CANCELED:
            self._orderqueue.popleft()

    def view(self) -> str:
        '''Returns a pretty-print view of the limit.'''
        return f'{self.price()} | {self.valid_orders():03d} | {self.volume():0>8f} | {self.notional()}'

    def __repr__(self) -> str:
        return f'Limit(price={self.price()}, n_orders={self.valid_orders()}, notional={self.notional()})'

    #### RELATED TO FAKE ORDERS

    def fakeorder_exists(self) -> bool:
        '''True if limit contains a fake order.'''
        return self._fakeorder is not None

    def set_fakeorder(self, order: Order) -> None:
        '''Set `order` as the new limit fake order. This method first deletes the previous order.'''
        self.delete_fakeorder()
        self._fakeorder = order
        self.enqueue(self._fakeorder)

    def delete_fakeorder(self) -> None:
        '''Deletes the current fake order, if no fake order is set it does nothing.'''
        if self._fakeorder is None: return
        self.cancel_order(self._fakeorder)
        self._fakeorder = None

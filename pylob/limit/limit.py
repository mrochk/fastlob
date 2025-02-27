from decimal import Decimal
from collections import deque

from pylob.order import Order
from pylob.enums import OrderStatus
from pylob.utils import zero

class Limit:
    '''
    A limit is a collection of limit orders sitting at a certain price.
    '''
    _price: Decimal
    _volume: Decimal
    _valid_orders: int
    _orderqueue: deque[Order]

    def __init__(self, price: Decimal):
        '''
        Args:
            price (num): The price at which the limit will sit.
        '''
        self._price = price
        self._volume = zero()
        self._valid_orders = 0
        self._orderqueue = deque()

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

    def notional(self) -> Decimal:
        return self.price() * self.volume()

    def valid_orders(self) -> int:
        '''Getter for limit size (number of orders).

        Returns:
            int: The size of the limit.
        '''
        return self._valid_orders

    def empty(self) -> bool:
        '''Check if limit **contains zero valid orders**, not if the limit queue is empty.

        Returns:
            bool: True if limit is empty.
        '''
        return self.valid_orders() == 0

    def deepempty(self): 
        '''Check if limit **contains zero orders**.

        Returns:
            bool: True if limit is empty.
        '''
        return len(self._orderqueue) == 0

    def next_order(self) -> Order:
        '''Returns the next order to be matched by an incoming market order.

        Returns:
            Order: The next order to be executed.
        '''
        self._prune_canceled()
        return self._orderqueue[0]

    def enqueue(self, order: Order):
        '''Add (enqueue) an order in limit.

        Args:
            order (Order): The order to add.
        '''
        self._orderqueue.append(order)
        order.set_status(OrderStatus.PENDING)

        self._volume += order.quantity()
        self._valid_orders += 1

    def fill_next(self, quantity: Decimal):
        '''**Partially** fill the next order in the queue. Filling it entirely would lead to problems, to only use in 
        last stage of order execution (i.e: `_partial_fill_order`).

        Args:
            quantity (Decimal): The quantity to fill the order with.
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

    def cancel_order(self, order: Order):
        '''Cancel an order.

        Args:
            order (Order): The order to cancel.
        '''
        self._volume -= order.quantity()
        self._valid_orders -= 1

        order.set_status(OrderStatus.CANCELED)

    def _prune_canceled(self):
        '''Pop the next order while it is a canceled one.'''
        # this method should not use any other method to ensure no infinite recursion
        while not self.deepempty() and self._orderqueue[0].canceled(): 
            self._orderqueue.popleft()

    def view(self) -> str:
        return f'{self.price()} | {self.valid_orders():03d} | {self.volume():0>8f} | {self.notional()}'

    def __repr__(self) -> str:
        return f'Limit(price={self.price()}, orders={self.valid_orders()}, notional={self.notional()})'

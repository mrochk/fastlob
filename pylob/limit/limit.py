from decimal import Decimal
from collections import deque

from pylob.enums import OrderSide, OrderStatus
from pylob.order import Order


class Limit:
    '''
    A limit is a collection of limit orders sitting at a certain price.
    '''
    _valid_orders: int
    _price: Decimal
    _side: OrderSide
    _volume: Decimal
    _orderqueue: deque[Order]
    _ordermap: dict[str, Order]

    def __init__(self, price: Decimal, side: OrderSide):
        '''
        Args:
            price (num): The price at which the limit will sit.
            side (OrderSide): The side of the limit.
        '''
        self._price = price
        self._side = side
        self._volume = Decimal(0)
        self._orderqueue = deque()
        self._ordermap = dict()
        self._valid_orders = 0

    def partial_fill_next(self, quantity: Decimal):
        order = self.get_next_order()
        assert order.quantity() > quantity

        order.set_status(OrderStatus.PARTIAL)
        order.fill(quantity)
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

    def valid_orders(self) -> int:
        '''Getter for limit size (number of orders).

        Returns:
            int: The size of the limit.
        '''
        return self._valid_orders

    def empty(self) -> bool:
        '''Check if limit is empty.

        Returns:
            bool: True if limit is empty.
        '''
        return self.volume() == 0 or self.valid_orders() == 0

    def add_order(self, order: Order):
        '''Add (enqueue) an order to the limit.

        Args:
            order (Order): The order to add.
        '''
        self._ordermap[order.id()] = order
        self._orderqueue.append(order)
        self._volume += order.quantity()
        self._valid_orders += 1
        order.set_status(OrderStatus.IN_LINE)

    def order_exists(self, order_id: str) -> bool:
        '''Returns true if an order with the given id is in the limit.

        Args:
            order_id (str): The id of the order to look for.

        Returns:
            bool: True if order is present in limit false otherwise.
        '''
        return order_id in self._ordermap.keys()

    def get_order(self, order_id: str) -> Order:
        '''Returns the order with the corresponding id.

        Args:
            order_id (str): The id of the order.

        Returns:
            Order: The order having such identifier.
        '''
        return self._ordermap[order_id]

    def get_next_order(self) -> Order:
        '''Returns the next order to be matched by an incoming market order.

        Returns:
            Order: The next order to be executed.
        '''
        self.prune_canceled_orders()
        return self._orderqueue[0]

    def delete_next_order(self) -> None:
        '''Pop from the queue the next order to be executed.
        '''
        self.prune_canceled_orders()
        order = self._orderqueue.popleft()
        self._volume -= order.quantity()
        del self._ordermap[order.id()]
        self._valid_orders -= 1

    def cancel_order(self, order: Order):
        self.order.set_status(OrderStatus.CANCELED)
        self._volume -= order.quantity()
        self._valid_orders -= 1

    def prune_canceled_orders(self):
        while not self.empty() and self._orderqueue[0].canceled():
            self.delete_next_order()

    def __repr__(self) -> str:
        p, s, v = self.price(), self.valid_orders(), self.volume()
        return f'{self.side().name}Limit(price={p}, orders={s}, volume={v})'

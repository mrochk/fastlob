from decimal import Decimal
from collections import deque

from pylob import todecimal
from pylob.order import Order
from pylob.consts import num

class Limit:
    '''
    A limit is a collection of orders.
    '''
    price : Decimal
    orders : deque[Order]

    def __init__(self, price : num):
        self.price = todecimal(price)
        self.orders = deque()
        self.orders_set = set()

    def add_order(self, order : Order) -> bool:
        # do not add order is price is different
        if self.price != order.price: return False

        # do not add same order two times
        if order.identifier in self.orders_set: return False

        # add order id to set and order to queue
        self.orders_set.add(order.identifier)
        self.orders.append(order)
        return True

    def size(self) -> int: return len(self.orders)

    def display_orders(self) -> None: print(self.orders)

    def __repr__(self) -> str:
        return f'Limit(p={self.price}, size={len(self.orders)})'
from decimal import Decimal
from collections import deque
from typing import Optional

from pylob import todecimal
from pylob.order import Order
from pylob.consts import num

class Limit:
    '''
    A limit is a collection of orders.
    '''
    price    : Decimal
    volume   : Decimal
    orderq   : deque[Order]
    ordermap : dict[Order]

    def __init__(self, price : num):
        self.price = todecimal(price)
        self.volume = Decimal(0)
        self.orderq = deque()
        self.ordermap = dict()

    def add_order(self, order : Order) -> bool:
        # do not add order if qty <= 0
        if order.quantity <= 0: return False

        # do not add order is price is different
        if self.price != order.price: return False

        # do not add same order two times
        if order.identifier in self.ordermap.keys(): return False

        # add order
        self.ordermap[order.identifier] = order
        self.orderq.append(order)

        # add volume
        self.volume = self.volume + order.quantity

        return True

    def get_order(self, identifier : int) -> Optional[Order]:
        if identifier in self.ordermap: return self.ordermap[identifier]
        return None

    def size(self) -> int: return len(self.orderq)

    def display_orders(self) -> None: print(self.orderq)

    def sanity_check(self) -> bool:
        '''
        Check if price correct for all orders, 
        no duplicates and all of same type.
        '''
        is_bid = self.orderq[0].is_bid() 

        for order in self.orderq:
            if order.price != self.price: return False
            if order.is_bid() != is_bid: return False

        return True

    def __repr__(self) -> str:
        p = self.price
        size = len(self.orderq)
        volume = self.volume
        return f'Limit(p={p}, size={size}, vol={volume})'
'''
The matching engine module, could also be a static class.
'''

from pylob import OrderType
from pylob.limit import Limit
from pylob.side import Side
from pylob.order import Order

def execute(order : Order, side : Side):
    '''
    Execute a market order.
    '''
    lim : Limit = side.best()

    while order.quantity() > lim.volume():
        order.partial_fill(lim.volume())
        side.remove_limit(lim.price())
        lim = side.best()

    lim_order = lim.next_order()

    while order.quantity > lim_order.quantity():
        order.partial_fill(lim_order.quantity())
        lim.pop_next_order()
        lim_order = lim.next_order()

    lim_order.partial_fill(order.quantity())

    assert(order.quantity == 0)

def place(order : Order, side : Side):
    '''
    Place a limit order.
    '''
    if not side.limit_exists(order.price):
        side.add_limit(order.price())
    side.add_order(order)
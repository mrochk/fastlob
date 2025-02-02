from pylob import OrderType
from pylob.limit import Limit
from pylob.side import Side
from pylob.order import Order

class MatchingEngine:
    '''
    The matching-engine implements all the logic
    related to executing market orders.
    It is not responsible for checking that the operation
    can be performed or not, only executing it.
    '''
    def __init__(self):
        pass

    def execute(self, order : Order, side : Side):
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

    def place(self, order : Order, side : Side):
        if not side.limit_exists(order.price):
            side.add_limit(order.price())
        side.add_order(order)
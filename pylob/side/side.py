import io
from abc import ABC
from decimal import Decimal
from sortedcollections import SortedDict

from pylob.enums import OrderSide
from pylob.order import Order
from pylob.consts import zero
from pylob.limit import Limit


class Side(ABC):
    '''A side is a collection of limits, whose ordering by price depends if it 
    is the bid side, or the ask side.
    '''
    _limits: SortedDict[Decimal, Limit]
    _orders: dict[int, Order]
    _side: OrderSide
    _volume: Decimal

    def __init__(self):
        self._orders = dict()
        self._volume = zero()

    def size(self) -> int:
        '''Get number of limits in the side.

        Returns:
            int: The number of limits.
        '''
        return len(self._limits)

    def empty(self) -> bool:
        '''Check if side is empty (does not contain any limit).

        Returns:
            bool: True is side is empty.
        '''
        return self.size() == 0

    def side(self) -> OrderSide:
        '''Get the side of the limit.

        Returns:
            OrderSide: The side of the limit.
        '''
        return self._side

    def best(self) -> Limit:
        '''Get the best limit of the side.

        Returns:
            Limit: The best limit.
        '''
        return self._limits.peekitem(0)[1]

    def add_limit(self, price: Decimal) -> None:
        '''Add a limit to the side.

        Args:
            price (Decimal): The price at which a limit should be created.
        '''
        self._limits[price] = Limit(price, self.side())

    def price_exists(self, price: Decimal) -> bool:
        '''Check there is a limit at a certain price.

        Args:
            price (Decimal): The price level to check.

        Returns:
            bool: True if such limit exists.
        '''
        return price in self._limits.keys()

    def get_limit(self, price: Decimal) -> Limit:
        '''Get the limit sitting at a certain price.

        Args:
            price (Decimal): The price level of the limit to get.

        Returns:
            Limit: The limit sitting at the given price level.
        '''
        return self._limits[price]

    def place_order(self, order: Order) -> None:
        '''Place an order in the side at its corresponding limit.

        Args:
            order (Order): The order to place.
        '''
        self._limits[order.price()] = order
        self._orders[order.id()] = order
        self._volume += order.quantity()

    def get_order(self, order_id: int) -> Order:
        '''Get an order by its identifier.

        Args:
            order_id (int): The order identifier.

        Returns:
            Order: The order having such identifier.
        '''
        return self._orders[order_id]

    def remove_order(self, order_id: int) -> None:
        '''Remove an order by its identifier.

        Args:
            order_id (int): The order identifier.
        '''
        order = self.get_order(order_id)
        self._volume -= order.quantity()
        del self._orders[order_id]

        if self.get_limit(order.price()).empty():
            del self._limits[order.price()]


class BidSide(Side):
    '''The bid side, where the best price level is the highest.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

    def __repr__(self):
        # TODO: Rewrite
        def mkline(lim): return ' - ' + str(lim) + '\n'
        buffer = io.StringIO()
        i = 0
        for bidlim in self._limits.values():
            if i > 10:
                if i < self.size():
                    buffer.write(f'...({self.size() - 10} more bids)\n')
                break
            i += 1
            buffer.write(mkline(bidlim))
        return buffer.getvalue()


class AskSide(Side):
    '''The bid side, where the best price level is the lowest.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.ASK
        self._limits = SortedDict()

    def __repr__(self):
        # TODO: Rewrite
        def mkline(lim): return ' - ' + str(lim) + '\n'
        buffer = io.StringIO()
        ten_asks = list()
        i = 0
        for asklim in self._limits.values():
            if i > 10:
                break
            i += 1
            ten_asks.append(asklim)

        if self.size() > 10:
            buffer.write(f'...({self.size() - 10} more asks)\n')

        for asklim in reversed(ten_asks):
            length = buffer.write(mkline(asklim)) - 2

        return buffer.getvalue()

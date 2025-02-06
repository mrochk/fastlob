from abc import ABC
from decimal import Decimal
from sortedcollections import SortedDict

from pylob import OrderSide
from pylob.order import Order
from pylob.consts import num
from pylob.limit import Limit
from pylob import todecimal

class Side(ABC):
    '''
    A side is a collection of limits, whose ordering by price depends if it is 
    a BidSide or AskSide.
    '''
    _limits : SortedDict[Decimal, Limit]
    _side   : OrderSide

    def fill_best(self):
        best = self.best()
        best.match_all()
        del self._limits[best.price()]

    def get_limit(self, price : Decimal) -> Limit:
        assert isinstance(price, Decimal)
        return self._limits[price]

    def side(self) -> OrderSide: 
        '''Getter for side.

        Returns:
            OrderSide: The "side" of the Side object.
        '''
        return self._side

    def limits(self): 
        '''

        Returns:
            _type_: _description_
        '''
        return self._limits.values()

    def size(self) -> int: 
        '''Getter for number of limits.

        Returns:
            int: The number of limits sitting in the Side.
        '''
        return len(self._limits.keys())

    def best(self) -> Limit: 
        '''The best limit in the side.

        Returns:
            Limit: The best limit in the side, lowest if AskSide, highest for
            BidSide.
        '''
        return self._limits.peekitem(0)[1]

    def volume(self) -> Decimal: 
        '''Getter for volume.

        Returns:
            Decimal: The sum of the volumes of all limits in the Side. 
        '''
        Sum = Decimal(0)
        lim : Limit
        for lim in self.limits(): Sum += lim.volume()
        return Sum

    def prices(self) -> set: 
        '''Getter for all prices in the side.

        Returns:
            set: A set containing every unique price level.
        '''
        return self._limits.keys()

    def limit_exists(self, price : num) -> bool: 
        '''Check if limit is in the side.

        Args:
            price (num): The limit price level to check.

        Returns:
            bool: True if there is a limit at this price. 
        '''
        return price in self._limits

    def add_limit(self, price : num) -> None: 
        '''Add a limit to the side at a given price.

        Args:
            price (num): The price at which the limit should be added.

        Raises:
            ValueError: If there is already a limit at this price level.
        '''
        if self.limit_exists(price): 
            raise ValueError(f'price {price} already in side')

        self._limits[price] = Limit(price, self.side())

    def add_limit_if_not_exists(self, price : num):
        if not self.limit_exists(price):
            self.add_limit(price)

    def add_order(self, order : Order): 
        '''Add an order to the side.

        Args:
            order (Order): The limit order to add.

        Raises:
            ValueError: If there is no limit for the order required price level.
        '''
        lim : Limit = self._limits.get(order.price())

        if lim is None:
            raise ValueError(f'order price {order.price()} not in side')

        lim.add_order(order)

    def remove_limit(self, price : num) -> None:
        '''Remove a limit sitting in the side.

        Args:
            price (num): The price level to remove.

        Raises:
            ValueError: If there is no such limit.
        '''
        if not self.limit_exists(price): 
            raise ValueError(f'price {price} not in side')

        del self._limits[price]

class BidSide(Side):
    '''The bid side, where the best price level is the highest. '''
    def __init__(self):
        self._side   = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

class AskSide(Side):
    '''The bid side, where the best price level is the lowest. '''
    def __init__(self):
        self._side   = OrderSide.ASK
        self._limits = SortedDict()
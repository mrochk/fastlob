import io, abc, threading
from decimal import Decimal
from sortedcollections import SortedDict

from fastlob.limit import Limit
from fastlob.order import Order
from fastlob.utils import zero
from fastlob.enums import OrderSide

class Side(abc.ABC):
    '''A side is a collection of limits, whose ordering by price depends if it is the bid or ask side.'''

    _side: OrderSide
    _volume: Decimal
    _limits: SortedDict[Decimal, Limit]
    _mutex: threading.Lock 
    # ^ the role of this mutex is to prevent a limit order being canceled meanwhile we are matching a market order
    # it must be locked by any other class before it can execute or canel an order in the side 

    def __init__(self): 
        self._volume = zero()
        self._mutex = threading.Lock()

    def lock(self): return self._mutex

    def side(self) -> OrderSide:
        '''Get the side of the limit.'''
        return self._side

    def volume(self) -> Decimal:
        '''Getter for side volume, that is the sum of the volume of all limits.'''
        return self._volume

    def size(self) -> int:
        '''Get number of limits in the side.'''
        return len(self._limits)

    def empty(self) -> bool:
        '''Check if side is empty (does not contain any limit).'''
        return self.size() == 0

    def best(self) -> Limit:
        '''Get the best limit of the side.'''
        return self._limits.peekitem(0)[1]

    def place(self, order: Order) -> None:
        '''Place an order in the side at its corresponding limit.'''
        price = order.price()
        self._new_price_if_not_exists(price)
        self._get_limit(price).enqueue(order)
        self._volume += order.quantity()

    def cancel_order(self, order: Order) -> None:
        '''Cancel an order sitting in the side.'''
        self._volume -= order.quantity()
        lim = self._get_limit(order.price())
        lim.cancel_order(order)
        if lim.empty(): del self._limits[lim.price()]

    def _get_limit(self, price: Decimal) -> Limit:
        '''Get the limit sitting at a certain price.'''
        return self._limits[price]

    def _price_exists(self, price: Decimal) -> bool:
        '''Check there is a limit at a certain price.'''
        return price in self._limits.keys()

    def _new_price(self, price: Decimal) -> None:
        '''Add a limit to the side.'''
        self._limits[price] = Limit(price)

    def _new_price_if_not_exists(self, price: Decimal) -> None:
        '''Create price level if not exists.'''
        if not self._price_exists(price): self._new_price(price)

    def __repr__(self) -> str:
        if self.empty(): return f'{self.side().name}Side(size={self.size()}, volume={self.volume()})'
        return f'{self.side().name}Side(size={self.size()}, volume={self.volume()}, best={self.best()})'

    @abc.abstractmethod
    def view(self, n : int) -> str: pass

class BidSide(Side):
    '''The bid side, where the best price level is the highest.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.BID
        self._limits = SortedDict(lambda x: -x)

    def view(self, n : int = 10) -> str:
        if self.empty(): return str()

        buffer = io.StringIO()
        count = 0
        for bidlim in self._limits.values():
            if count >= n:
                if count < self.size():
                    buffer.write(f"   ...({self.size() - n} more bids)\n")
                break
            buffer.write(f" - {bidlim.view()}\n")
            count += 1

        return buffer.getvalue()

class AskSide(Side):
    '''The bid side, where the best price level is the lowest.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.ASK
        self._limits = SortedDict()

    def view(self, n : int = 10) -> str:
        if self.empty(): return str()

        buffer = io.StringIO()
        if self.size() > n: buffer.write(f"   ...({self.size() - n} more asks)\n")
        count = 0
        l = list()
        for asklim in self._limits.values():
            if count >= n: break
            l.append(f" - {asklim.view()}\n")
            count += 1

        buffer.writelines(reversed(l))
        return buffer.getvalue()

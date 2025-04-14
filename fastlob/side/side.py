'''The Side is a collection of limits, whose ordering (by price) depends wether it is a bid or ask side.'''

import io
import abc
import threading
from numbers import Number
from typing import Optional, Iterable
from decimal import Decimal
from collections.abc import Sequence
from sortedcollections import SortedDict

from fastlob.limit import Limit
from fastlob.order import Order, BidOrder, AskOrder, OrderParams
from fastlob.utils import zero, todecimal
from fastlob.enums import OrderSide, OrderType

from .utils import check_snapshot_pair, check_update_pair

class Side(abc.ABC):
    '''The Side is a collection of limits, whose ordering (by price) depends wether it is a bid or ask side.'''

    _side: OrderSide
    _volume: Decimal
    _price2limits: SortedDict[Decimal, Limit]
    _mutex: threading.Lock
    # ^ the role of this mutex is to prevent a limit order being canceled meanwhile we are matching a market order
    # it must be locked by any other class before it can execute or cancel an order in the side

    def __init__(self):
        self._volume = zero()
        self._mutex = threading.Lock()

    def lock(self):
        '''Returns the side mutex lock.'''

        return self._mutex

    def side(self) -> OrderSide:
        '''Get the side of the limit.'''

        return self._side

    def volume(self) -> Decimal:
        '''Getter for side volume, that is the sum of the volume of all limits.'''

        return self._volume

    def update_volume(self, update: Decimal) -> None:
        '''Add `update` to current side volume.'''

        self._volume += update

    def size(self) -> int:
        '''Get number of limits in the side.'''

        return len(self._price2limits)

    def empty(self) -> bool:
        '''Check if side is empty (does not contain any limit).'''

        return self.size() == 0

    def best(self) -> Limit:
        '''Get the best limit of the side.'''

        return self._price2limits.peekitem(0)[1]

    def best_limits(self, n: int) -> list[tuple[Decimal, Decimal, int]]:
        '''Returns a triplet (price, volume, #orders) for the best `n` price levels.'''

        result = list()

        for i, lim in enumerate(self.limits()):
            if i >= n: break
            t = (lim.price(), lim.volume(), lim.valid_orders())
            result.append(t)

        return result

    def limits(self) -> Sequence:
        '''Get all limits (sorted).'''

        return self._price2limits.values()

    def place(self, order: Order) -> None:
        '''Place an order in the side at its corresponding limit.'''

        price = order.price()
        self._new_price_if_not_exists(price)
        self.get_limit(price).enqueue(order)
        self._volume += order.quantity()

    def cancel_order(self, order: Order) -> None:
        '''Cancel an order sitting in the side.'''

        self._volume -= order.quantity()
        lim = self.get_limit(order.price())
        lim.cancel_order(order)
        if lim.empty(): del self._price2limits[lim.price()]

    def get_limit(self, price: Decimal) -> Limit:
        '''Get the limit sitting at a certain price.'''

        return self._price2limits[price]

    def pop_limit(self, price) -> None:
        '''Delete a limit from the side.'''

        self._price2limits.pop(price) # remove limit from side

    def check_market_order(self, order: Order) -> Optional[str]:
        '''Check if a market order is valid.'''

        match order.otype():
            case OrderType.FOK: # check that order quantity can be filled
                if not self.immediately_matched(order):
                    return 'FOK bid order is not immediately matchable'
        return None

    def _price_exists(self, price: Decimal) -> bool:
        '''Check there is a limit at a certain price.'''

        return price in self._price2limits.keys()

    def _new_price(self, price: Decimal) -> None:
        '''Create a new price level in the side.'''

        self._price2limits[price] = Limit(price)

    def _new_price_if_not_exists(self, price: Decimal) -> None:
        '''Create new price level if doesn't exist.'''

        if not self._price_exists(price): self._new_price(price)

    def __repr__(self) -> str:
        if self.empty(): return f'{self.side().name}Side(size={self.size()}, volume={self.volume()})'
        return f'{self.side().name}Side(size={self.size()}, volume={self.volume()}, best={self.best()})'

    @abc.abstractmethod
    def is_market(self, order: Order) -> bool:
        '''Check if an order of the opposite side is market.'''

    @abc.abstractmethod
    def immediately_matched(self, order: Order) -> bool:
        '''Check that a market order (of the opposite side) can be immediately matched. This function is useful
        when checking that a FOK order is valid.'''

    @abc.abstractmethod
    def apply_snapshot(self, snapshot: Iterable[tuple[Number, Number]]):
        '''Initialize side with predefined volume for price levels.'''

    @abc.abstractmethod
    def apply_updates(self, updates: Iterable[tuple[Number, Number]]):
        '''Apply price level updates to side.'''

    @abc.abstractmethod
    def view(self, n : int) -> str:
        '''Get a pretty-printed view of the side.'''

    #### RELATED TO FAKE ORDERS

    def place_fakeorder(self, order: Order):
        '''Place a fake order in the side.'''

        if not self._price_exists(order.price()):
            self._new_price(order.price())

        limit = self.get_limit(order.price())
        prev_limit_volume = limit.volume()

        limit.set_fakeorder(order)
        self.update_volume(limit.volume() - prev_limit_volume)

    def delete_fakeorder(self, price: Decimal):
        '''Delete a fake order at price level `price`.'''

        if not self._price_exists(price): return

        limit = self.get_limit(price)
        if not limit.fakeorder_exists(): return

        limit.delete_fakeorder()
        if limit.volume() == 0.0: self.pop_limit(price)

class BidSide(Side):
    '''The bid side, where **the best price level is the highest**.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.BID
        self._price2limits = SortedDict(lambda x: -x)

    def is_market(self, order: AskOrder) -> bool:
        if self.empty(): return False
        if self.best().price() >= order.price(): return True
        return False

    def immediately_matched(self, order: AskOrder) -> bool:
        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()

        lim : Limit
        for lim in self.limits():
            if lim.price() < order.price(): break
            if volume >= order.quantity(): break
            volume += lim.volume()

        if volume < order.quantity(): return False
        return True

    def apply_snapshot(self, bids):
        # apply snapshot (init side) to askside
        for pair in bids:
            check_snapshot_pair(pair)
            price, volume = pair

            params = OrderParams(OrderSide.BID, price, volume, OrderType.FAKE)
            order  = BidOrder(params)
            self.place_fakeorder(order)

    def apply_updates(self, bids):
        # apply updates to bid side
        for pair in bids:
            check_update_pair(pair)
            price, volume = pair

            price  = todecimal(price)
            volume = todecimal(volume)

            if volume == 0:
                self.delete_fakeorder(price)
                continue

            params = OrderParams(OrderSide.BID, price, volume, OrderType.FAKE)
            order  = BidOrder(params)
            self.place_fakeorder(order)

    def view(self, n : int = 10) -> str:
        if self.empty(): return str()

        buffer = io.StringIO()
        count = 0
        for bidlim in self._price2limits.values():
            if count >= n:
                if count < self.size():
                    buffer.write(f"   ...({self.size() - n} more bids)\n")
                break
            buffer.write(f" - {bidlim.view()}\n")
            count += 1

        return buffer.getvalue()

class AskSide(Side):
    '''The bid side, where **the best price level is the lowest**.'''

    def __init__(self):
        super().__init__()
        self._side = OrderSide.ASK
        self._price2limits = SortedDict()

    def is_market(self, order: BidOrder) -> bool:
        if self.empty(): return False
        if self.best().price() <= order.price(): return True
        return False

    def immediately_matched(self, order: BidOrder) -> bool:
        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()
        limits = self.limits()

        lim : Limit
        for lim in limits:
            if lim.price() > order.price(): break
            if volume >= order.quantity(): break
            volume += lim.volume()

        if volume < order.quantity(): return False
        return True

    def apply_snapshot(self, asks):
        # apply snapshot (init side) to askside
        for pair in asks:
            check_snapshot_pair(pair)
            price, volume = pair

            params = OrderParams(OrderSide.ASK, price, volume, OrderType.FAKE)
            order  = AskOrder(params)
            self.place_fakeorder(order)

    def apply_updates(self, asks):
        # apply updates to ask side
        for pair in asks:
            check_update_pair(pair)
            price, volume = pair

            price  = todecimal(price)
            volume = todecimal(volume)

            if volume == 0:
                self.delete_fakeorder(price)
                continue

            params = OrderParams(OrderSide.ASK, price, volume, OrderType.FAKE)
            order  = AskOrder(params)
            self.place_fakeorder(order)

    def view(self, n : int = 10) -> str:
        if self.empty(): return str()

        buffer = io.StringIO()
        if self.size() > n: buffer.write(f"   ...({self.size() - n} more asks)\n")
        count = 0
        l = list()
        for asklim in self._price2limits.values():
            if count >= n: break
            l.append(f" - {asklim.view()}\n")
            count += 1

        buffer.writelines(reversed(l))
        return buffer.getvalue()

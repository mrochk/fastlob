'''Main module containing the Orderbook class.'''

import io
import time
import logging
import threading
from decimal import Decimal
from typing import Optional, Iterable
from sortedcollections import SortedDict
from termcolor import colored

from fastlob import engine
from fastlob.side import AskSide, BidSide
from fastlob.order import OrderParams, Order, AskOrder, BidOrder
from fastlob.enums import OrderSide, OrderStatus, OrderType
from fastlob.result import ResultBuilder, ExecutionResult
from fastlob.utils import time_asint
from fastlob.consts import DEFAULT_LIMITS_VIEW

from .utils import not_running_error, check_limit_order

class Orderbook:
    '''
    The `Orderbook` is a collection of bid and ask limits. 
    It is reponsible for:
    - Calling `engine` when order is market.
    - Placing order when order is limit.
    - All the safety checking.
    '''

    _name: str
    _askside: AskSide
    _bidside: BidSide
    _orders: dict[str, Order]
    _expirymap: SortedDict
    _start_time: int
    _alive: bool
    _logger: logging.Logger
    _updates: Iterable[dict]

    def __init__(self, name: Optional[str] = 'LOB-1', start: Optional[bool] = False):
        '''
        Args:
            name (Optional[str]): Defaults to "LOB".
        '''
        self._name       = name
        self._askside    = AskSide()
        self._bidside    = BidSide()
        self._orders     = dict()
        self._expirymap  = SortedDict()
        self._start_time = None
        self._alive      = False
        self._updates    = None

        self._logger = logging.getLogger(f'[{name}]')
        self._logger.info('lob initialized, ready to be started using <ob.start>')

        if start: self.start()

    #### MAIN FUNCS

    def start(self):
        '''Start the lob.'''

        def clean_expired_orders():
            while self._alive:
                self._cancel_expired_orders()
                time.sleep(0.1) # what value to set here ? maybe it should depend on the size of the book

        self._alive = True
        self._start_time = time_asint()
        self._logger.info('starting background GTD orders manager..')
        threading.Thread(target=clean_expired_orders).start()
        self._logger.info('lob started properly, ready to receive orders')

    def stop(self):
        '''Stop the lob.'''

        if not self._alive:
            self._logger.error('lob is not running')
            return

        self._alive = False
        self._start_time = None
        self._logger.info('lob stopped properly')

    def reset(self) -> None:
        '''Reset the lob.'''

        if self._alive:
            self._logger.error('lob must be stopped (using <ob.stop>) before reset can be called')
            return

        self.__init__(self._name)

    def __call__(self, order_params: OrderParams | Iterable[OrderParams]) -> ExecutionResult | list[ExecutionResult]:
        '''Process one or many orders: equivalent to calling `process_one` or `process_many`.'''

        if not isinstance(order_params, Iterable):
            return self.process_one(order_params)

        return self.process_many(order_params)

    def process_many(self, orders_params: Iterable[OrderParams]) -> list[ExecutionResult]:
        '''Process many orders at once.

        Args:
            orders_params (Iterable[OrderParams]): Orders to create and process.
        '''
        if not self._alive:
            return [not_running_error(self._logger).build() for _ in orders_params]

        return [self.process_one(params) for params in orders_params]

    def process_one(self, order_params: OrderParams) -> ExecutionResult:
        '''Creates and processes the order corresponding to the corresponding order params.'''

        if not self._alive:
            return not_running_error(self._logger).build()

        if not isinstance(order_params, OrderParams):
            result = ResultBuilder.new_error()
            errmsg = 'order_params is not an instance of fastlob.OrderParams'
            result.add_message(errmsg); self._logger.error(errmsg)
            return result.build()

        #                                         (params const already checks that expiry is set)
        if order_params.otype == OrderType.GTD and order_params.expiry <= (t := time_asint()):
            result = ResultBuilder.new_error()
            errmsg = f'GTD order must expire in the future (but {order_params.expiry} <= {t})'
            result.add_message(errmsg); self._logger.error(errmsg)
            return result.build()

        self._logger.info('processing order params')

        match order_params.side:
            case OrderSide.ASK:
                order = AskOrder(order_params)
                result = self._process_ask_order(order)

            case OrderSide.BID:
                order = BidOrder(order_params)
                result = self._process_bid_order(order)

        if result.success():
            self._logger.info('order %s was processed successfully', order.id())
            self._save_order(order, result)

        else: self._logger.warning('order was not successfully processed')

        if order.status() == OrderStatus.PARTIAL:
            msg = f'order {order.id()} partially filled by engine, {order.quantity()} placed at {order.price()}'
            self._logger.info(msg)
            result.add_message(msg)

        return result.build()

    def cancel(self, orderid: str) -> ExecutionResult:
        '''Cancel an order sitting in the lob given its id.'''

        if not self._alive:
            return not_running_error(self._logger).build()

        self._logger.info('attempting to cancel order with id %s', orderid)

        result = ResultBuilder.new_cancel(orderid)

        try: order = self._orders[orderid]
        except KeyError:
            result.set_success(False)
            errmsg = f'order {orderid} not found in lob'
            result.add_message(errmsg)
            self._logger.warning(errmsg)
            return result.build()

        if not order.valid():
            result.set_success(False)
            errmsg = f'order {orderid} can not be canceled (status={order.status()})'
            result.add_message(errmsg)
            self._logger.warning(errmsg)
            return result.build()

        self._logger.info('order %s can be canceled', orderid)

        match order.side():
            case OrderSide.BID:
                with self._bidside.lock():
                    self._logger.info('cancelling bid order %s', orderid)
                    self._bidside.cancel_order(order)

            case OrderSide.ASK:
                with self._askside.lock():
                    self._logger.info('cancelling ask order %s', orderid)
                    self._askside.cancel_order(order)

        msg = f'order {order.id()} canceled properly'
        result.set_success(True)
        result.add_message(msg)
        self._logger.info(msg)
        return result.build()

    def running_time(self) -> int:
        '''Get time since lob is running.'''

        if not self._alive: return 0
        return time_asint() - self._start_time

    def best_asks(self, n: int) -> list[tuple[Decimal, Decimal, int]]:
        '''Return best `n` asks (price, volume, #orders) triplets. If `n > #asks`, returns `#asks` elements.'''

        if (nasks := self.n_asks()) < n:
            self._logger.warning('asking for %s limits in <ob.best_asks> but lob only contains %s', n, nasks)

        return self._askside.best_limits(n)

    def best_bids(self, n: int) -> list[tuple[Decimal, Decimal, int]]:
        '''Return best `n` bids (price, volume, #orders) triplets. If `n > #bids`, returns `#bids` elements.'''

        if (nbids := self.n_bids()) < n:
            self._logger.warning('asking for %s limits in <ob.best_bids> but lob only contains %s', n, nbids)

        return self._bidside.best_limits(n)

    def best_ask(self) -> Optional[tuple[Decimal, Decimal, int]]:
        '''Get the best ask limit=(price, volume, #orders) in the lob.'''

        if self._askside.empty():
            self._logger.warning('calling <ob.best_ask> but lob does not contain ask limits')
            return None

        lim = self._askside.best()
        return lim.price(), lim.volume(), lim.valid_orders()

    def best_bid(self) -> Optional[tuple[Decimal, Decimal, int]]:
        '''Get the best bid limit=(price, volume, #orders) in the lob.'''

        if self._bidside.empty():
            self._logger.warning('calling <ob.best_bid> but lob does not contain ask limits')
            return None

        lim = self._bidside.best()
        return lim.price(), lim.volume(), lim.valid_orders()

    def n_bids(self) -> int:
        '''Get the number of bids limits.'''

        return self._bidside.size()

    def n_asks(self) -> int:
        '''Get the number of asks limits.'''

        return self._askside.size()

    def n_prices(self) -> int:
        '''Get the total number of limits (price levels).'''

        return self.n_asks() + self.n_bids()

    def bids_volume(self) -> Decimal:
        '''Total volume on the bid side.'''

        return self._bidside.volume()

    def asks_volume(self) -> Decimal:
        '''Total volume on the ask side.'''

        return self._askside.volume()

    def midprice(self) -> Optional[Decimal]:
        '''Get the lob midprice.'''

        if self._askside.empty() or self._bidside.empty():
            self._logger.warning('calling <ob.midprice> but lob does not contain limits on both sides')
            return None

        askprice, bidprice = self.best_ask()[0], self.best_bid()[0]
        return Decimal(0.5) * (askprice + bidprice)

    def spread(self) -> Decimal:
        '''Get the lob spread.'''

        if self._askside.empty() or self._bidside.empty():
            self._logger.warning('calling <ob.spread> but lob does not contain limits on both sides')
            return None

        askprice, bidprice = self.best_ask()[0], self.best_bid()[0]
        return askprice - bidprice

    def get_status(self, orderid: str) -> Optional[tuple[OrderStatus, Decimal]]:
        '''Get the status and the quantity left for a given order or None if order was not accepted by the lob.'''

        try:
            order = self._orders[orderid]
            self._logger.info('order %s found in lob', orderid)
            return order.status(), order.quantity()
        except KeyError:
            self._logger.warning('order %s not found in lob', orderid)
            return None

    def view(self, n : int = DEFAULT_LIMITS_VIEW) -> str:
        '''Get a pretty-printed view of the lob state.'''

        length = 40
        if not self._bidside.empty(): length = len(self._bidside.best().view()) + 2
        elif not self._askside.empty(): length = len(self._askside.best().view()) + 2

        buffer = io.StringIO()
        buffer.write(f"   [ORDER-BOOK {self._name.upper()}]\n\n")
        buffer.write(colored(self._askside.view(n), "red"))
        buffer.write(' ' + '~'*length + '\n')
        buffer.write(colored(self._bidside.view(n), "green"))

        if self._askside.empty() or self._bidside.empty():
            return buffer.getvalue()

        footer =  f'\n - spread = {self.spread()}'
        footer += f' | midprice = {self.midprice()}'
        footer += f'\n - asks volume = {self.asks_volume()}'
        footer += f' | bids volume = {self.bids_volume()}'

        buffer.write(colored(footer, color='blue'))

        return buffer.getvalue()

    def render(self) -> None:
        '''Pretty-print the lob.'''

        print(self.view(), flush=True)

    def __repr__(self) -> str:
        buffer = io.StringIO()
        buffer.write(f'Order-book {self._name}\n')
        buffer.write(f'- started={self._alive}\n')
        buffer.write(f'- running-time={self.running_time()}s\n')
        buffer.write(f'- #prices={self.n_prices()}\n')
        buffer.write(f'- #asks={self.n_asks()}\n')
        buffer.write(f'- #bids={self.n_bids()}')
        return buffer.getvalue()

    #### SNAPSHOT RELATED FUNCS

    @staticmethod
    def from_snapshot(snapshot: dict, name: Optional[str] = 'LOB', start: Optional[bool] = False):
        '''
        Instantiate a new LOB from a given snapshot. A "snapshot" is a dictionary of the following 
        form `{"bids": <list_of_(price, volume)_pairs>, "asks": <list_of_(price, volume)_pairs>}`.

        It does so by placing a "fake" order. These orders are also not added to the history. 
        They are simply added to each price level.

        Returns:
            Orderbook: A new LOB initialized with `snapshot`.
        '''

        if not isinstance(snapshot, dict) or snapshot.keys() != {'bids', 'asks'}:
            raise ValueError('snapshot must be a dictionary containing "bids" and "asks" keys')

        if not isinstance(snapshot['bids'], Iterable) or not isinstance(snapshot['asks'], Iterable):
            raise ValueError('snapshot[bids|asks] must be an iterable of (price, volume) pairs')

        lob = Orderbook(name=name, start=False)

        asks, bids = snapshot['asks'], snapshot['bids']

        lob._askside.apply_snapshot(asks)
        lob._bidside.apply_snapshot(bids)

        if start: lob.start()
        return lob

    #### UPDATES RELATED FUNCS

    def load_updates(self, updates: Iterable[dict]):
        '''Load `updates` so that every time `step` is called, the lob gets updated (using fake orders).'''

        if not isinstance(updates, Iterable):
            raise ValueError(
                'updates must be an Iterable of dicts of the form ' + 
                '{"bids|asks": <iterable_of_(price, volume)_pairs>}')

        self._updates = iter(updates)

    def step(self):
        '''Apply the updates in `next(updates)` to the lob.'''

        if self._updates is None:
            self._logger.warning('calling <ob.step> but nothing was loaded using <ob.load_updates>')
            return

        try: updates = next(self._updates)
        except StopIteration:
            self._logger.warning('calling <ob.step> but iterator is exhausted')
            return

        if not isinstance(updates, dict) or updates.keys() != {'bids', 'asks'}:
            raise ValueError('updates must be a dictionary containing "bids" and "asks" keys')

        bids, asks = updates['bids'], updates['asks']

        # lock all to aply updates
        with self._askside.lock(), self._bidside.lock():

            # apply updates to ask side
            self._askside.apply_updates(asks)

            # apply updates to bid side
            self._bidside.apply_updates(bids)

    #### AUXILIARY FUNCS (where most of the work happens)

    def _process_bid_order(self, order: BidOrder) -> ResultBuilder:
        self._logger.info('processing bid order %s', order.id())

        if self._askside.is_market(order):
            self._logger.info('bid order %s is market', order.id())

            if (error := self._askside.check_market_order(order)) is not None:
                order.set_status(OrderStatus.ERROR)
                result = ResultBuilder.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            # execute the order
            with self._askside.lock():
                result = engine.execute(order, self._askside)

            if not result.success():
                self._logger.error('bid market order %s could not be executed by engine', order.id())
                return result

            if order.status() == OrderStatus.PARTIAL:
                with self._bidside.lock():
                    self._bidside.place(order)
                    msg = f'order {order.id()} partially executed, {order.quantity()} was placed as a bid limit order'
                    self._logger.info(msg)
                    result.add_message(msg)

            self._logger.info('executed bid market order %s', order.id())
            return result

        # else: is limit order
        self._logger.info('bid order %s is limit', order.id())

        result = ResultBuilder.new_limit(order.id())

        if (error := check_limit_order(order)) is not None:
            order.set_status(OrderStatus.ERROR)
            result.set_success(False)
            result.add_message(error)
            self._logger.warning(error)
            return result

        # place the order in the side
        with self._bidside.lock(): self._bidside.place(order)

        result.set_success(True)
        self._logger.info('order %s successfully placed', order.id())
        return result

    def _process_ask_order(self, order: AskOrder) -> ResultBuilder:
        self._logger.info('processing ask order %s', order.id())

        if self._bidside.is_market(order):
            self._logger.info('ask order %s is market', order.id())

            if (error := self._bidside.check_market_order(order)) is not None:
                order.set_status(OrderStatus.ERROR)
                result = ResultBuilder.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            # execute the order
            with self._bidside.lock():
                result = engine.execute(order, self._bidside)

            if not result.success():
                self._logger.error('ask market order %s could not be executed by engine', order.id())
                return result

            if order.status() == OrderStatus.PARTIAL:
                with self._askside.lock():
                    self._askside.place(order)
                    msg = f'order {order.id()} partially executed, {order.quantity()} was placed as an ask limit order'
                    self._logger.info(msg)
                    result.add_message(msg)

            self._logger.info('executed ask market order %s', order.id())
            return result

        # else is limit order
        self._logger.info('ask order %s is limit', order.id())

        result = ResultBuilder.new_limit(order.id())

        if (error := check_limit_order(order)) is not None:
            order.set_status(OrderStatus.ERROR)
            result.set_success(False)
            result.add_message(error)
            self._logger.warning(error)
            return result

        # place the order in the side
        with self._askside.lock(): self._askside.place(order)

        result.set_success(True)
        self._logger.info('order %s successfully placed', order.id())
        return result

    def _save_order(self, order: Order, result: ResultBuilder):
        self._logger.info('adding order to history')
        self._orders[order.id()] = order

        if order.otype() == OrderType.GTD: # and result._KIND == ResultType.LIMIT:
            # <- TODO: doesnt work in the case where the order is a partially filling market (then placed in limit),
            # but how to not add market orders then ?
            self._logger.info('order is a limit GTD order, adding order to expiry map')
            if order.expiry() not in self._expirymap.keys(): self._expirymap[order.expiry()] = list()
            self._expirymap[order.expiry()].append(order)

    def _cancel_expired_orders(self):
        '''Background expired orders cleaner.'''

        timestamps = self._expirymap.keys()
        if not timestamps: return

        now = time_asint()
        keys_outdated = filter(lambda timestamp: timestamp < now, timestamps)

        for key in keys_outdated:
            expired_orders = self._expirymap[key]

            self._logger.info('GTD orders: cancelling %s with t=%s', len(expired_orders), key)

            for order in expired_orders:
                if not order.valid(): continue

                match order.side():
                    case OrderSide.ASK:
                        with self._askside.lock(): self._askside.cancel_order(order)

                    case OrderSide.BID:
                        with self._bidside.lock(): self._bidside.cancel_order(order)

            del self._expirymap[key]

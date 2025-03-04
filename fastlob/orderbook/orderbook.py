import io, time, logging, threading
from sortedcollections import SortedDict
from typing import Optional, Iterable
from decimal import Decimal
from termcolor import colored

from fastlob import engine
from fastlob.side import AskSide, BidSide
from fastlob.limit import Limit
from fastlob.order import OrderParams, Order, AskOrder, BidOrder
from fastlob.enums import OrderSide, OrderStatus, OrderType
from fastlob.result import ExecutionResult
from fastlob.utils import zero, time_asint
from fastlob.consts import DEFAULT_LIMITS_VIEW

class Orderbook:
    '''The `OrderBook` is a collection of bid and ask limits. It is reponsible for calling the matching engine, placing
    limit orders, and safety checking.'''

    _name: str
    _ask_side: AskSide
    _bid_side: BidSide
    _orders: dict[str, Order]
    _expirymap: SortedDict
    _start_time: int
    _logger: logging.Logger

    def __init__(self, name: Optional[str] = None, log_level: int = logging.WARNING):
        self._name = name if name else ""
        self._ask_side = AskSide()
        self._bid_side = BidSide()
        self._orders = dict()
        self._expirymap = SortedDict()
        self._start_time = None
        self._alive = False

        logging.basicConfig(level=log_level)
        self._logger = logging.getLogger(f'orderbook[{name}]')
        self._logger.level = log_level

        self._logger.info('ob initialized, ready to be started')

    def reset(self) -> None: 
        if self._alive:
            self._logger.error('ob must be stopped (using ob.stop()) before reset can be called')
            return

        self.__init__(self._name)

    def start(self):
        '''Start the order-book.'''

        def loop():
            while self._alive:
                self._cancel_expired_orders()
                time.sleep(0.9)

        self._alive = True
        self._start_time = time_asint()

        self._logger.info('starting background GTD orders manager')
        threading.Thread(target=loop).start()

        self._logger.info('ob started properly')

    def stop(self): 
        '''Stop the order-book.'''

        self._alive = False
        self._start_time = None
        self._logger.info('ob stopped properly')

    def __call__(self, order_params: OrderParams | Iterable[OrderParams]) -> ExecutionResult | list[ExecutionResult]:
        '''Process one or many orders: equivalent to calling `process_one` or `process_many`.'''

        if isinstance(order_params, OrderParams): return self.process_one(order_params)
        return self.process_many(order_params)

    def process_one(self, order_params: OrderParams) -> ExecutionResult:
        '''Creates and processes the order corresponding to the corresponding arguments.'''

        if not self._alive: 
            self._logger.error('is not running (ob.start() must be called before it can be used)')
            return None

        self._logger.info('processing order params')

        match order_params.side:
            case OrderSide.BID: order = BidOrder(order_params)
            case OrderSide.ASK:  order = AskOrder(order_params)

        return self._process_order(order)

    def process_many(self, orders_params: Iterable[OrderParams]) -> list[ExecutionResult]:
        '''Process many orders at once.

        Args:
            orders_params (Iterable[OrderParams]): Orders to create and process.
        '''
        return [self.process_one(params) for params in orders_params]

    def cancel_order(self, order_id: str) -> ExecutionResult:
        if not self._alive: 
            self._logger.error('is not running (start() must be called before it can be used)')
            return None

        self._logger.info(f'attempting to cancel order with id {order_id}')

        result = ExecutionResult.new_cancel(order_id)

        try: order = self._orders[order_id]
        except KeyError: 
            result.set_success(False)
            result.add_message('<orderbook>: order not in orderbook')
            self._logger.error('order not in orderbook')
            return result

        if not order.valid(): 
            result.set_success(False)
            result.add_message(f'<orderbook>: order can not be canceled (status={order.status()})')
            self._logger.error(f'order can not be canceled (status={order.status()})')
            return result

        match order.side():
            case OrderSide.BID: 
                with self._bid_side._mutex: self._bid_side.cancel_order(order)

            case OrderSide.ASK: 
                with self._ask_side._mutex: self._ask_side.cancel_order(order)

        result.set_success(True)
        result.add_message(f'<orderbook>: order {order.id()} canceled properly')
        self._logger.info(f'<orderbook>: order {order.id()} canceled properly')

        return result

    def running_since(self) -> int: 
        '''Get time since order-book is running.'''

        if not self._alive: return 0
        return time_asint() - self._start_time

    def best_ask(self) -> Optional[Decimal]:
        '''Get the best ask price in the book.'''

        try: return self._ask_side.best().price()
        except: 
            self._logger.error('calling ob.best_ask() but book does not contain ask limits')
            return None

    def best_bid(self) -> Optional[Decimal]:
        '''Get the best bid price in the book.'''

        try: return self._bid_side.best().price()
        except: 
            self._logger.error('calling ob.best_bid() but book does not contain bid limits')
            return None

    def n_bids(self) -> int:
        '''Get the number of bids limits in the book.'''

        return self._bid_side.size()

    def n_asks(self) -> int:
        '''Get the number of asks limits in the book.'''

        return self._ask_side.size()

    def n_prices(self) -> int:
        '''Get the total number of limits (price levels) in the book.'''

        return self.n_asks() + self.n_bids()

    def midprice(self) -> Optional[Decimal]:
        '''Get the order-book mid-price.'''

        try:
            best_ask, best_bid = self.best_ask(), self.best_bid()
            return Decimal(0.5) * (best_ask + best_bid)
        except:
            self._logger.error('calling ob.midprice() but book does not contain limits on both sides')
            return None

    def spread(self) -> Decimal:
        '''Get the order-book spread.'''

        try: return self.best_ask() - self.best_bid()
        except:
            self._logger.error('calling ob.spread() but book does not contain limits on both sides')
            return None

    def get_order_status(self, order_id: str) -> Optional[tuple[OrderStatus, Decimal]]:
        '''Get the status and the quantity left for a given order or None if order was not accepted by the ob.'''

        try: 
            order = self._orders[order_id]
            self._logger.info(f'order {order_id} found in book')
            return order.status(), order.quantity()
        except KeyError: 
            self._logger.warning(f'order {order_id} not found in book')
            return None

    def _process_order(self, order: Order) -> ExecutionResult:
        '''**Place or execute** the given order depending on its price level.'''

        self._logger.info(f'executing order with id {order.id()}')

        result : ExecutionResult
        match order.side():
            case OrderSide.BID: result = self._process_order_bid(order)
            case OrderSide.ASK: result = self._process_order_ask(order)
              
        if result.success(): 
            self._logger.info(f'order {order.id()} was executed successfully')

            self._orders[order.id()] = order # add order to ob dict

            if order.otype() == OrderType.GTD: 

                self._logger.info(f'order is GTD, adding order to expiry map')

                if order.expiry() not in self._expirymap.keys(): self._expirymap[order.expiry()] = list()
                self._expirymap[order.expiry()].append(order)

        else: self._logger.warning(f'order was not successfully executed')

        if order.status() == OrderStatus.PARTIAL:
            self._logger.info(f'order partially filled by engine, {order.quantity()} placed at {order.price()}')
            msg = f'<orderbook>: order partially filled by engine, {order.quantity()} placed at {order.price()}'
            result.add_message(msg)

        return result

    def _process_order_bid(self, order: Order):
        self._logger.info(f'order {order.id()} is bid order')

        if self._is_market_bid(order):

            self._logger.info(f'order {order.id()} is market order')

            if (error := self._check_bid_market_order(order)) is not None: 
                result = ExecutionResult.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            # execute order
            with self._ask_side._mutex:
                result = engine.execute(order, self._ask_side)

            if order.status() == OrderStatus.PARTIAL: 
                with self._bid_side._mutex: 
                    self._bid_side.place(order)
                    self._logger.info(f'order {order.id()} partially executed, rest was placed as limit order')

            self._logger.info(f'finished executing market order {order.id()}')

            return result

        else: # is limit order
            self._logger.info(f'order {order.id()} is limit order')
            if (error := self._check_limit_order(order)): return error

            # place order
            with self._bid_side._mutex: self._bid_side.place(order)

            self._logger.info(f'order {order.id()} successfully placed')

            result = ExecutionResult.new_limit(order.id())
            result.set_success(True)

            return result

    def _process_order_ask(self, order: Order):
        self._logger.info(f'order {order.id()} is ask order')

        if self._is_market_ask(order):
            self._logger.info(f'order {order.id()} is market order')

            if (error := self._check_ask_market_order(order)) is not None: 
                result = ExecutionResult.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            # execute the order
            with self._bid_side._mutex:
                result = engine.execute(order, self._bid_side)

            if order.status() == OrderStatus.PARTIAL: 
                with self._ask_side._mutex: self._ask_side.place(order)
                self._logger.info(f'order {order.id()} partially executed, rest was placed as limit order')

            self._logger.info(f'finished executing market order {order.id()}')

            return result

        else: # is limit order
            self._logger.info(f'order {order.id()} is limit order')
            if (error := self._check_limit_order(order)): return error

            # place the order in the side
            with self._ask_side._mutex: self._ask_side.place(order)

            self._logger.info(f'order {order.id()} successfully placed')

            result = ExecutionResult.new_limit(order.id())
            result.set_success(True)

            return result

    def _is_market_bid(self, order):
        if self._ask_side.empty(): return False
        if self.best_ask() <= order.price(): return True
        return False

    def _is_market_ask(self, order):
        if self._bid_side.empty(): return False
        if self.best_bid() >= order.price(): return True
        return False

    def _check_limit_order(self, order: Order) -> Optional[str]:
        match order.otype():

            case OrderType.FOK: # FOK order can not be a limit order by definition
                order.set_status(OrderStatus.ERROR)
                self._logger.warning(f'FOK order {order.id()} is not immediately matchable')
                return 'FOK order must be immediately matchable'

            case _: return None

    def _check_bid_market_order(self, order: Order) -> Optional[str]:
        match order.otype():

            case OrderType.FOK: # check that order quantity can be filled
                return self._check_fok_bid_market_order(order)

            case _: return None

    def _check_ask_market_order(self, order : Order) -> Optional[str]:
        match order.otype():

            case OrderType.FOK: # check that order quantity can be filled
                return self._check_fok_ask_order(order)

            case _: return None

    def _check_fok_bid_market_order(self, order) -> Optional[str]:
        result = None

        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()
        limits = self._ask_side._limits.values()

        lim : Limit
        for lim in limits:
            if lim.price() > order.price(): break
            if volume >= order.quantity():  break
            volume += lim.volume()

        if volume < order.quantity(): 
            result = self._fok_error_quantity(order)
            order.set_status(OrderStatus.ERROR)
            self._logger.warning(f'FOK order {order.id()} is not immediately matchable, order qty too big')

        return result

    def _check_fok_ask_order(self, order) -> Optional[str]:
        result = None

        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()
        limits = self._bid_side._limits.values()

        lim : Limit
        for lim in limits:
            if lim.price() < order.price(): break
            if volume >= order.quantity():  break
            volume += lim.volume()

        if volume < order.quantity(): 
            result = self._fok_error_quantity(order)
            order.set_status(OrderStatus.ERROR)
            self._logger.warning(f'FOK order {order.id()} is not immediately matchable, order qty too big')

        return result

    def _fok_error_price(self, order: Order) -> str:
        return f'<orderbook>: FOK {order.side().name} order can not be executed at this price ({order.price()})'

    def _fok_error_quantity(self, order: Order) -> str:
        return f'<orderbook>: FOK {order.side().name} order can not be executed for this quantity ({order.quantity()})'

    def _cancel_expired_orders(self):
        timestamps = self._expirymap.keys()

        if not timestamps: return

        now = time_asint()
        keys_outdated = filter(lambda timestamp: timestamp < now, timestamps)

        for key in keys_outdated:
            expired_orders = self._expirymap[key]

            self._logger.info(f'GTD orders manager: cancelling {len(expired_orders)} with t={key}')

            for order in expired_orders:
                if not order.valid(): continue

                match order.side():
                    case OrderSide.ASK: 
                        with self._ask_side._mutex: self._ask_side.cancel_order(order)

                    case OrderSide.BID: 
                        with self._bid_side._mutex: self._bid_side.cancel_order(order)

            del self._expirymap[key]

    def view(self, n : int = DEFAULT_LIMITS_VIEW) -> str:
        '''Outputs the order-book in the following format:\n

        Order-book <pair>:
        - ...
        - AskLimit(price=.., size=.., vol=..)
        -------------------------------------
        - BidLimit(price=.., size=.., vol=..)
        - ...

        `n` controls the number of limits to display on each side
        '''
        length = 40
        if not self._bid_side.empty(): length = len(self._bid_side.best().view()) + 2
        elif not self._ask_side.empty(): length = len(self._ask_side.best().view()) + 2

        buffer = io.StringIO()
        buffer.write(f"   [ORDER-BOOK {self._name}]\n\n")
        buffer.write(colored(self._ask_side.view(n), "red"))
        buffer.write(' ' + '~'*length + '\n')
        buffer.write(colored(self._bid_side.view(n), "green"))

        if self._ask_side.empty() or self._bid_side.empty(): return buffer.getvalue()

        buffer.write(colored(f"\n    Spread = {self.spread()}", color="blue"))
        buffer.write(colored(f", Mid-price = {self.midprice()}", color="blue"))

        return buffer.getvalue()

    def render(self) -> None: 
        '''Pretty-print.'''
        print(self.view(), flush=True)

    def __repr__(self) -> str:
        buffer = io.StringIO()
        buffer.write(f'Order-Book {self._name}\n')
        buffer.write(f'- started={self._alive}\n')
        buffer.write(f'- running_time={self.running_since()}s\n')
        buffer.write(f'- #prices={self.n_prices()}\n')
        buffer.write(f'- #asks={self.n_asks()}\n')
        buffer.write(f'- #bids={self.n_bids()}')
        return buffer.getvalue()
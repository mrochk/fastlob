import io, time, logging, threading
from decimal import Decimal
from sortedcollections import SortedDict
from typing import Optional, Iterable
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
    '''The `Orderbook` is a collection of bid and ask limits. It is reponsible for calling the matching engine, placing
    limit orders, and safety checking.'''

    _NAME: str
    _ask_side: AskSide
    _bid_side: BidSide
    _orders: dict[str, Order]
    _expirymap: SortedDict
    _start_time: int
    _alive: bool
    _logger: logging.Logger

    def __init__(self, name: Optional[str] = 'LOB-1', log_level: int = logging.WARNING):
        '''
        Args:
            name (Optional[str]): Name of the LOB. Defaults to "LOB-1".
            log_level (int): One of logging.[INFO, WARNING, ERROR]. Defaults to WARNING.
        '''
        self._NAME       = name
        self._ask_side   = AskSide()
        self._bid_side   = BidSide()
        self._orders     = dict()
        self._expirymap  = SortedDict()
        self._start_time = None
        self._alive      = False

        logging.basicConfig(level=log_level)
        self._logger = logging.getLogger(f'orderbook[{name}]')
        self._logger.level = log_level
        self._logger.info('initialized, ready to be started (using ob.start())')

    def start(self):
        '''Properly start the limit-order-book.'''

        def clean_expired_orders():
            while self._alive: 
                self._cancel_expired_orders()
                time.sleep(0.9)

        self._alive = True
        self._start_time = time_asint()
        self._logger.info('starting background GTD orders manager')
        threading.Thread(target=clean_expired_orders).start()
        self._logger.info('ob started properly')

    def stop(self): 
        '''Stop the limit-order-book.'''

        self._alive = False
        self._start_time = None
        self._logger.info('ob stopped properly')

    def reset(self) -> None: 
        '''Reset the limit-order-book.'''

        if self._alive:
            errmsg = 'must be stopped (using ob.stop()) before reset can be called'
            self._logger.error(errmsg)
            return

        self.__init__(self._NAME)

    def __call__(self, order_params: OrderParams | Iterable[OrderParams]) -> ExecutionResult | list[ExecutionResult]:
        '''Process one or many orders: equivalent to calling `process_one` or `process_many`.'''

        if not isinstance(order_params, list): return self.process_one(order_params)
        return self.process_many(order_params)

    def process_many(self, orders_params: Iterable[OrderParams]) -> list[ExecutionResult]:
        '''Process many orders at once.

        Args:
            orders_params (Iterable[OrderParams]): Orders to create and process.
        '''
        return [self.process_one(params) for params in orders_params]

    def process_one(self, order_params: OrderParams) -> ExecutionResult:
        '''Creates and processes the order corresponding to the corresponding order params.'''

        if not self._alive: 
            result = ExecutionResult.new_error()
            errmsg = f'{self._NAME} is not running (ob.start() must be called before it can be used)'
            result.add_message(errmsg); self._logger.error(errmsg)
            return result

        if not isinstance(order_params, OrderParams):
            result = ExecutionResult.new_error()
            errmsg = 'order_params is not an instance of fastlob.OrderParams'
            result.add_message(errmsg); self._logger.error(errmsg)
            return result

        self._logger.info('processing order params')

        match order_params.side:
            case OrderSide.ASK: 
                order = AskOrder(order_params)
                result = self._process_ask_order(order)

            case OrderSide.BID: 
                order = BidOrder(order_params)
                result = self._process_bid_order(order)

        if result.success(): 
            self._logger.info(f'order {order.id()} was processed successfully')
            self._save_order(order)

        else: self._logger.warning(f'order was not successfully processed')

        if order.status() == OrderStatus.PARTIAL:
            msg = f'order {order.id()} partially filled by engine, {order.quantity()} placed at {order.price()}'
            self._logger.info(msg)
            result.add_message(msg)

        return result

    def cancel(self, order_id: str) -> ExecutionResult:
        if not self._alive: 
            errmsg = f'{self._NAME} is not running (start() must be called before it can be used)'
            self._logger.error(errmsg)
            result = ExecutionResult.new_error()
            result.add_message(errmsg)
            return result

        self._logger.info(f'attempting to cancel order with id {order_id}')

        result = ExecutionResult.new_cancel(order_id)

        try: order = self._orders[order_id]
        except KeyError: 
            result.set_success(False)
            errmsg = f'order {order_id} not in lob'
            result.add_message(errmsg)
            self._logger.error(errmsg)
            return result

        if not order.valid(): 
            result.set_success(False)
            errmsg = f'order {order_id} can not be canceled (status={order.status()})'
            result.add_message(errmsg)
            self._logger.warning(errmsg)
            return result

        self._logger.info(f'order {order_id} can be canceled')

        match order.side():
            case OrderSide.BID: 
                with self._bid_side.lock(): 
                    self._logger.info(f'cancelling bid order {order_id}')
                    self._bid_side.cancel_order(order)

            case OrderSide.ASK: 
                with self._ask_side.lock(): 
                    self._logger.info(f'cancelling ask order {order_id}')
                    self._ask_side.cancel_order(order)

        msg = f'order {order.id()} canceled properly'
        result.set_success(True)
        result.add_message(msg)
        self._logger.info(msg)
        return result

    def log_level(self) -> int: return self._logger.level

    def set_log_level(self, log_level: int) -> None: 
        logging.basicConfig(level=log_level)
        self._logger.level = log_level

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
        '''Get the number of bids limits.'''

        return self._bid_side.size()

    def n_asks(self) -> int:
        '''Get the number of asks limits.'''

        return self._ask_side.size()

    def n_prices(self) -> int:
        '''Get the total number of limits (price levels).'''

        return self.n_asks() + self.n_bids()

    def midprice(self) -> Optional[Decimal]:
        '''Get the mid-price.'''

        try:
            best_ask, best_bid = self.best_ask(), self.best_bid()
            return Decimal(0.5) * (best_ask + best_bid)
        except:
            self._logger.error('calling ob.midprice() but book does not contain limits on both sides')
            return None

    def spread(self) -> Decimal:
        '''Get the spread.'''

        try: return self.best_ask() - self.best_bid()
        except:
            self._logger.error('calling ob.spread() but book does not contain limits on both sides')
            return None

    def get_status(self, order_id: str) -> Optional[tuple[OrderStatus, Decimal]]:
        '''Get the status and the quantity left for a given order or None if order was not accepted by the lob.'''

        try: 
            order = self._orders[order_id]
            self._logger.info(f'order {order_id} found in book')
            return order.status(), order.quantity()
        except KeyError: 
            self._logger.warning(f'order {order_id} not found in book')
            return None
    
    def _process_bid_order(self, order: BidOrder) -> ExecutionResult:
        self._logger.info(f'processing bid order {order.id()}')

        if self._is_market_bid(order):
            self._logger.info(f'bid order {order.id()} is market')

            if (error := self._check_bid_market_order(order)) is not None: 
                order.set_status(OrderStatus.ERROR)
                result = ExecutionResult.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            with self._ask_side.lock():
                result = engine.execute(order, self._ask_side)

            if not result.success():
                self._logger.error(f'bid market order {order.id()} could not be executed by engine')
                return result

            if order.status() == OrderStatus.PARTIAL: 
                with self._bid_side.lock(): 
                    self._bid_side.place(order)
                    msg = f'order {order.id()} partially executed, rest was placed as a bid limit order'
                    self._logger.info(msg)
                    result.add_message(msg)

            self._logger.info(f'executed bid market order {order.id()}')
            return result

        else:
            self._logger.info(f'bid order {order.id()} is limit')

            result = ExecutionResult.new_limit(order.id())

            if (error := self._check_limit_order(order)) is not None: 
                order.set_status(OrderStatus.ERROR)
                result.set_success(False)
                result.add_message(error)
                self._logger.error(error)
                return result

            with self._bid_side.lock(): self._bid_side.place(order)

            result.set_success(True)
            self._logger.info(f'order {order.id()} successfully placed')
            return result

    def _process_ask_order(self, order: AskOrder) -> ExecutionResult:
        self._logger.info(f'processing ask order {order.id()}')

        if self._is_market_ask(order):
            self._logger.info(f'ask order {order.id()} is market')

            if (error := self._check_ask_market_order(order)) is not None: 
                order.set_status(OrderStatus.ERROR)
                result = ExecutionResult.new_market(order.id())
                result.set_success(False)
                result.add_message(error)
                return result

            # execute the order
            with self._bid_side.lock():
                result = engine.execute(order, self._bid_side)

            if order.status() == OrderStatus.PARTIAL: 
                with self._ask_side.lock(): self._ask_side.place(order)
                self._logger.info(f'order {order.id()} partially executed, rest was placed as limit order')

            self._logger.info(f'executed ask market order {order.id()}')
            return result

        else: # is limit order
            self._logger.info(f'order {order.id()} is limit order')

            result = ExecutionResult.new_limit(order.id())

            if (error := self._check_limit_order(order)) is not None: 
                order.set_status(OrderStatus.ERROR)
                result.set_success(False)
                result.add_message(error)
                self._logger.error(error)
                return error

            # place the order in the side
            with self._ask_side.lock(): self._ask_side.place(order)

            self._logger.info(f'order {order.id()} successfully placed')
            result.set_success(True)
            return result

    def _save_order(self, order):
        self._logger.info(f'adding order to dict')
        self._orders[order.id()] = order

        if order.otype() == OrderType.GTD: 
            self._logger.info(f'order is GTD, adding order to expiry map')
            if order.expiry() not in self._expirymap.keys(): self._expirymap[order.expiry()] = list()
            self._expirymap[order.expiry()].append(order)

    def _is_market_ask(self, order: AskOrder) -> bool:
        if self._bid_side.empty(): return False
        if self.best_bid() >= order.price(): return True
        return False

    def _is_market_bid(self, order: BidOrder) -> bool:
        if self._ask_side.empty(): return False
        if self.best_ask() <= order.price(): return True
        return False

    def _check_limit_order(self, order: Order) -> Optional[str]:
        match order.otype():
            case OrderType.FOK: # FOK order can not be a limit order by definition
                self._logger.error(f'FOK order {order.id()} is not immediately matchable')
                return 'FOK order is not immediately matchable'

        return None

    def _check_bid_market_order(self, order: BidOrder) -> Optional[str]:
        match order.otype():
            case OrderType.FOK: # check that order quantity can be filled
                if not self._immediately_matchable_bid(order):
                    return 'FOK bid order is not immediately matchable' 

        return None

    def _check_ask_market_order(self, order: AskOrder) -> Optional[str]:
        match order.otype():
            case OrderType.FOK: # check that order quantity can be filled
                if not self._immediately_matchable_ask(order):
                    return 'FOK ask order is not immediately matchable' 

        return None

    def _immediately_matchable_bid(self, order: BidOrder) -> bool:
        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()
        limits = self._ask_side._limits.values()

        lim : Limit
        for lim in limits:
            if lim.price() > order.price(): break
            if volume >= order.quantity():  break
            volume += lim.volume()

        if volume < order.quantity(): return False
        return True

    def _immediately_matchable_ask(self, order: AskOrder) -> bool:
        # we want the limit volume down to the order price to be >= order quantity
        volume = zero()
        limits = self._bid_side._limits.values()

        lim : Limit
        for lim in limits:
            if lim.price() < order.price(): break
            if volume >= order.quantity():  break
            volume += lim.volume()

        if volume < order.quantity(): return False
        return True

    def _cancel_expired_orders(self):
        '''Background expired orders cleaner.'''

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
                        with self._ask_side.lock(): self._ask_side.cancel_order(order)

                    case OrderSide.BID: 
                        with self._bid_side.lock(): self._bid_side.cancel_order(order)

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
        buffer.write(f"   [ORDER-BOOK {self._NAME}]\n\n")
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
        buffer.write(f'Order-Book {self._NAME}\n')
        buffer.write(f'- started={self._alive}\n')
        buffer.write(f'- running_time={self.running_since()}s\n')
        buffer.write(f'- #prices={self.n_prices()}\n')
        buffer.write(f'- #asks={self.n_asks()}\n')
        buffer.write(f'- #bids={self.n_bids()}')
        return buffer.getvalue()
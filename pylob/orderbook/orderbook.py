import io, time
from sortedcollections import SortedDict
from typing import Optional, Iterable
from decimal import Decimal
from termcolor import colored
import threading

from pylob import engine
from pylob.side import AskSide, BidSide
from pylob.limit import Limit
from pylob.order import OrderParams, Order, AskOrder, BidOrder
from pylob.enums import OrderSide, OrderStatus, OrderType
from pylob.utils import zero, time_asint
from pylob.consts import DEFAULT_LIMITS_VIEW
from .result import ExecutionResult, MarketResult, LimitResult, CancelResult

class OrderBook:
    '''The `OrderBook` is a collection of bid and ask limits. It is reponsible for calling the matching engine, placing
    limit orders, and safety checking.'''

    _name: str
    _ask_side: AskSide
    _bid_side: BidSide
    _orders: dict[str, Order]
    _expirymap: SortedDict
    _start_time: int

    def __init__(self, name: Optional[str] = None):
        '''
        Args:
            name (Optional[str]): A name for the order-book. Defaults to None.
        '''
        self._name = name if name else ""
        self._ask_side = AskSide()
        self._bid_side = BidSide()
        self._orders = dict()
        self._expirymap = SortedDict()
        self._start_time = time_asint()
        self._alive = False

    def reset(self) -> None: self.__init__(self._name)

    def start(self):
        '''Start the order-book, in fact this is simply starting the background GTD order manager.'''
        def loop():
            while self._alive:
                self._cancel_expired_orders()
                time.sleep(0.9)

        self._alive = True
        threading.Thread(target=loop).start()

    def stop(self): self._alive = False

    def __call__(self, order_params: OrderParams | Iterable[OrderParams]) -> ExecutionResult | list[ExecutionResult]:
        '''Process one or many orders: equivalent to calling `process_one` or `process_many`.'''
        if isinstance(order_params, OrderParams): return self.process_one(order_params)
        return self.process_many(order_params)

    def process_one(self, order_params: OrderParams) -> ExecutionResult:
        '''Creates and processes the order corresponding to the corresponding
        arguments.

        Args:
            order_params (OrderParams): Parameters of order to create and process.

        Returns:
            ExecutionResult: The result of processing the order params.
        '''
        order : Order
        match order_params.side:
            case OrderSide.BID: order = BidOrder(order_params)
            case OrderSide.ASK: order = AskOrder(order_params)

        return self._process_order(order)

    def process_many(self, orders_params: Iterable[OrderParams]) -> list[ExecutionResult]:
        '''Process many orders at once.

        Args:
            orders_params (Iterable[OrderParams]): Orders to create and process.
        '''
        return [self.process_one(params) for params in orders_params]

    def cancel_order(self, order_id: str) -> CancelResult:
        result = CancelResult(False)

        try: order = self._orders[order_id]
        except KeyError: 
            result.add_message(f'<orderbook>: order not in orderbook')
            return result

        if not order.valid(): 
            result.add_message(f'<orderbook>: order can not be canceled (status={order.status()})')
            return result

        match order.side():
            case OrderSide.BID: 
                with self._bid_side._mutex: self._bid_side.cancel_order(order)

            case OrderSide.ASK: 
                with self._ask_side._mutex: self._ask_side.cancel_order(order)

        result._success = True
        result.add_message(f'<orderbook>: order {order.id()} canceled properly')

        return result

    def clock(self) -> int: return time_asint() - self._start_time

    def best_ask(self) -> Decimal:
        '''Get the best ask price in the book.

        Returns:
            Decimal: The best ask price.
        '''
        return self._ask_side.best().price()

    def best_bid(self) -> Decimal:
        '''Get the best bid price in the book.

        Returns:
            Decimal: The best bid price.
        '''
        return self._bid_side.best().price()

    def n_bids(self) -> int:
        '''Get the number of bids limits in the book.

        Returns:
            int: The number of bids limits.
        '''
        return self._bid_side.size()

    def n_asks(self) -> int:
        '''Get the number of asks limits in the book.

        Returns:
            int: The number of asks limits.
        '''
        return self._ask_side.size()

    def n_prices(self) -> int:
        '''Get the total number of limits (price levels) in the book.

        Returns:
            int: Number of limits.
        '''
        return self.n_asks() + self.n_bids()

    def midprice(self) -> Decimal:
        '''Get the order-book mid-price.

        Returns:
            Decimal: (best_bid + best_ask) / 2
        '''
        best_ask, best_bid = self.best_ask(), self.best_bid()
        return Decimal(0.5) * (best_ask + best_bid)

    def spread(self) -> Decimal:
        '''Get the order-book spread.

        Returns:
            Decimal: best_ask - best_bid
        '''
        return self.best_ask() - self.best_bid()

    def get_order_status(self, order_id: str) -> Optional[tuple[OrderStatus, Decimal]]:
        '''Get the status and the quantity left for a given order, or None if order was not accepted by the book.'''
        try: 
            order = self._orders[order_id]
            return order.status(), order.quantity()
        except KeyError: return None

    def _process_order(self, order: Order) -> ExecutionResult:
        '''**Place or execute** the given order depending on its price level.'''

        result : MarketResult | LimitResult
        match order.side():
            case OrderSide.BID: result = self._process_order_bid(order)
            case OrderSide.ASK: result = self._process_order_ask(order)
              
        result._order_id = order.id()

        if result.success(): 
            self._orders[order.id()] = order

            if order.otype() == OrderType.GTD: 
                if order.expiry() not in self._expirymap.keys(): 
                    self._expirymap[order.expiry()] = list()
                self._expirymap[order.expiry()].append(order)

        if order.status() == OrderStatus.PARTIAL:
            msg = f'<orderbook>: order partially filled by engine, {order.quantity()} placed at {order.price()}'
            result.add_message(msg)

        return result

    def _process_order_bid(self, order):
        if self._is_market_bid(order):
            if (error := self._check_bid_market_order(order)): return error

            # execute order
            with self._ask_side._mutex:
                result = engine.execute(order, self._ask_side)

            if order.status() == OrderStatus.PARTIAL: 
                with self._bid_side._mutex: self._bid_side.place(order)

            return result

        else: # is limit order
            if (error := self._check_limit_order(order)): return error

            # place order
            with self._bid_side._mutex: self._bid_side.place(order)

            return LimitResult(True, order.id())

    def _process_order_ask(self, order):
        if self._is_market_ask(order):
            if (error := self._check_ask_market_order(order)): 
                print(error)
                return error

            # execute the order
            with self._bid_side._mutex:
                result = engine.execute(order, self._bid_side)

            if order.status() == OrderStatus.PARTIAL: 
                with self._ask_side._mutex: self._ask_side.place(order)

            return result

        else: # is limit order
            if (error := self._check_limit_order(order)): return error

            # place the order in the side
            with self._ask_side._mutex: self._ask_side.place(order)

            return LimitResult(True, order.id())

    def _is_market_bid(self, order):
        if self._ask_side.empty(): return False
        if self.best_ask() <= order.price(): return True
        return False

    def _is_market_ask(self, order):
        if self._bid_side.empty(): return False
        if self.best_bid() >= order.price(): return True
        return False

    def _FOK_error_price(self, order : Order) -> MarketResult:
        result = MarketResult(False)
        msg = f'<orderbook>: FOK {order.side().name} order can not be executed at this price ({order.price()})'
        result.add_message(msg)
        return result

    def _FOK_error_quantity(self, order : Order) -> MarketResult:
        result = MarketResult(False)
        msg = f'<orderbook>: FOK {order.side().name} order can not be executed for this quantity ({order.quantity()})'
        result.add_message(msg)
        return result

    def _check_limit_order(self, order : Order) -> Optional[LimitResult]:
        result = LimitResult(False)

        match order.otype():
          case OrderType.FOK: # FOK can not be a limit order by definition
              order.set_status(OrderStatus.ERROR)
              result.add_message('FOK order must be immediately matchable')
              return result
          case _: return None

    def _check_bid_market_order(self, order : Order) -> Optional[MarketResult]:
        match order.otype():
          case OrderType.FOK: # check that order quantity can be filled
              return self._check_FOK_bid_order(order)
          case _: return None

    def _check_ask_market_order(self, order : Order) -> Optional[MarketResult]:
        match order.otype():
          case OrderType.FOK: # check that order quantity can be filled
              return self._check_FOK_ask_order(order)
          case _: return None

    def _check_FOK_bid_order(self, order) -> Optional[MarketResult]:
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
            result = self._FOK_error_quantity(order)
            order.set_status(OrderStatus.ERROR)

        return result

    def _check_FOK_ask_order(self, order) -> Optional[MarketResult]:
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
            result = self._FOK_error_quantity(order)
            order.set_status(OrderStatus.ERROR)

        return result

    def _cancel_expired_orders(self):
        timestamps = self._expirymap.keys()

        if not timestamps: return

        now = time_asint()
        keys_outdated = filter(lambda timestamp: timestamp < now, timestamps)

        for key in keys_outdated:
            expired_orders = self._expirymap[key]
            print(f'cancelling {len(expired_orders)} with t={key}')
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

    def __repr__(self) -> str:
        if (self.n_bids() + self.n_asks()) > 1: return \
                f'OrderBook(name={self._name}, midprice={self.midprice()}, spread={self.spread()},' \
                + f'nprices={self.n_prices()}, nbids={self.n_bids()}, nasks={self.n_asks()}, clock={self.clock()})'
        return f'OrderBook(name={self._name}, nprices={self.n_prices()}, nbids={self.n_bids()}, ' \
            f'nasks={self.n_asks()}, clock={self.clock()})'
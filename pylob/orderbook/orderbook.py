import io
import os
import time
from typing import Optional, Iterable
from decimal import Decimal
from termcolor import colored

from pylob import engine
from pylob.limit import Limit
from pylob.utils import zero
from pylob.enums import OrderSide, OrderStatus, OrderType
from pylob.side import AskSide, BidSide
from pylob.order import OrderParams, Order, AskOrder, BidOrder
from .result import ExecutionResult, MarketResult, LimitResult, CancelResult

class OrderBook:
    '''The `OrderBook` is a collection of bid and ask limits. It is reponsible for calling the matching engine, placing
    limit orders, and safety checking.'''

    _name: str
    _ask_side: AskSide
    _bid_side: BidSide
    _orders: dict[str, Order]
    _start: float

    def __init__(self, name: Optional[str] = None):
        '''
        Args:
            name (Optional[str]): A name for the order-book. Defaults to None.
        '''
        self._name = name if name else ""
        self._ask_side = AskSide()
        self._bid_side = BidSide()
        self._orders = dict()
        self._start = time.time()

    def reset(self) -> None:
        self._ask_side = AskSide()
        self._bid_side = BidSide()
        self._orders = dict()
        self._start = time.time()

    def clock(self) -> float: return time.time() - self._start

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

    def get_order(self, order_id: str) -> Optional[tuple[OrderStatus, Decimal]]:
        try: 
            order = self._orders[order_id]
            return (order.status(), order.quantity())
        except KeyError: return None

    def __call__(self, order_params: OrderParams | Iterable[OrderParams]) -> ExecutionResult | list[ExecutionResult]:
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
            case OrderSide.BID: self._bid_side.cancel_order(order)
            case OrderSide.ASK: self._ask_side.cancel_order(order)

        result._success = True
        result.add_message(f'<orderbook>: order {order.id()} canceled properly')

        return result

    def _process_order(self, order: Order) -> ExecutionResult:
        '''**Place or execute** the given order depending on its price level.'''

        result : ExecutionResult

        match order.side():
            case OrderSide.BID:
                if self._is_market_bid(order):

                    error = self._check_bid_market_order(order)

                    if not error: # call matching engine
                        result = engine.execute(order, self._ask_side)
                        if order.status() == OrderStatus.PARTIAL: self._bid_side.place(order)
                    else: result = error

                else: # is limit order
                    error = self._check_limit_order(order)

                    if not error:
                        self._bid_side.place(order)
                        result = LimitResult(True, order.id())
                    else: result = error

            case OrderSide.ASK:
                if self._is_market_ask(order):

                    error = self._check_ask_market_order(order)

                    if not error: # call matching engine
                        result = engine.execute(order, self._bid_side)
                        if order.status() == OrderStatus.PARTIAL: self._ask_side.place(order)

                    else: result = error

                else: # is limit order

                    error = self._check_limit_order(order)

                    if not error:
                        self._ask_side.place(order)
                        result = LimitResult(True, order.id())

                    else: result = error

        if result.success(): self._orders[order.id()] = order

        if order.status() == OrderStatus.PARTIAL:
            msg = f"<orderbook>: order partially filled by engine, {order.quantity()} " f"placed at {order.price()}"
            result.add_message(msg)

        return result

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
                result.add_message(self._FOK_error_price(order))
                order.set_status(OrderStatus.ERROR)
                return result

            case _: return None

    def _check_bid_market_order(self, order : Order) -> Optional[MarketResult]:
        result = None

        match order.otype():

            case OrderType.FOK: # check that order quantity can be filled
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

            case _: return None


    def _check_ask_market_order(self, order : Order) -> Optional[MarketResult]:
        result = None

        match order.otype():

            case OrderType.FOK: # check that order quantity can be filled
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

            case _: return None

    def _is_market_bid(self, order):
        if self._ask_side.empty(): return False
        if self.best_ask() <= order.price(): return True
        return False

    def _is_market_ask(self, order):
        if self._bid_side.empty(): return False
        if self.best_bid() >= order.price(): return True
        return False

    def view(self) -> str:
        '''Outputs the order-book in the following format:\n

        Order-book <pair>:
        - ...
        - AskLimit(price=.., size=.., vol=..)
        -------------------------------------
        - BidLimit(price=.., size=.., vol=..)
        - ...
        '''
        if not self._bid_side.empty():
            length = len(self._bid_side.best().view()) + 2
        elif not self._ask_side.empty():
            length = len(self._ask_side.best().view()) + 2
        else: length = 40

        buffer = io.StringIO()
        buffer.write(f"   [ORDER-BOOK {self._name}]\n\n")
        buffer.write(colored(self._ask_side.view(), "red"))
        buffer.write(' ' + '~'*length + '\n')
        buffer.write(colored(self._bid_side.view(), "green"))

        if self._ask_side.empty() or self._bid_side.empty(): return buffer.getvalue()

        buffer.write(colored(f"\n    Spread = {self.spread()}", color="blue"))
        buffer.write(colored(f", Mid-price = {self.midprice()}", color="blue"))

        return buffer.getvalue()

    def __repr__(self) -> str:
        try: return \
                f'OrderBook(name={self._name}, midprice={self.midprice()}, spread={self.spread()},' \
                + f'nprices={self.n_prices()}, nbids={self.n_bids()}, nasks={self.n_asks()}, clock={self.clock()})'
        except: return \
                f'OrderBook(name={self._name}, nprices={self.n_prices()}, nbids={self.n_bids()}, ' \
                f'nasks={self.n_asks()}, clock={self.clock()})'
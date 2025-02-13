import io
import os
from typing import Optional, Iterable
from decimal import Decimal
from termcolor import colored

from pylob import engine
from pylob.enums import OrderSide, OrderStatus
from pylob.side import AskSide, BidSide
from pylob.order import OrderParams, Order, AskOrder, BidOrder
from .result import ExecutionResult, LimitResult, CancelResult

class OrderBook:
    '''The `OrderBook` is a collection of bid and ask limits. It is reponsible for calling the matching engine, placing
    limit orders, and safety checking.'''

    name: str
    ask_side: AskSide
    bid_side: BidSide
    id2order: dict[str, Order]

    def __init__(self, name: Optional[str] = None):
        '''
        Args:
            name (Optional[str]): A name for the order-book. Defaults to None.
        '''
        self.name = name if name else ""
        self.ask_side = AskSide()
        self.bid_side = BidSide()
        self.id2order = dict()

    ## GETTERS #####################################################################

    def best_ask(self) -> Decimal:
        '''Get the best ask price in the book.

        Returns:
            Decimal: The best ask price.
        '''
        return self.ask_side.best().price()

    def best_bid(self) -> Decimal:
        '''Get the best bid price in the book.

        Returns:
            Decimal: The best bid price.
        '''
        return self.bid_side.best().price()

    def n_bids(self) -> int:
        '''Get the number of bids limits in the book.

        Returns:
            int: The number of bids limits.
        '''
        return self.bid_side.size()

    def n_asks(self) -> int:
        '''Get the number of asks limits in the book.

        Returns:
            int: The number of asks limits.
        '''
        return self.ask_side.size()

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

    def get_order_status_qty(self, order_id: str) -> Optional[tuple[OrderStatus, Decimal]]:
        try: 
            order = self.id2order[order_id]
            return (order.status(), order.quantity())
        except KeyError: return None

    ################################################################################

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
        try: order = self.id2order[order_id]
        except KeyError: return CancelResult(False, "order not in orderbook")

        if not order.valid(): return CancelResult(False, f"order can not be canceled (status={order.status()})")

        match order.side():
            case OrderSide.BID: self.bid_side.cancel_order(order)
            case OrderSide.ASK: self.ask_side.cancel_order(order)

        return CancelResult(True, f"order {order.id()} canceled properly")

    def _process_order(self, order: Order) -> ExecutionResult:
        '''**Place or execute** the given order depending on its price level.'''
        result = None

        match order.side():
            case OrderSide.BID:
                if self._is_market(order):
                    result = engine.execute(order, self.ask_side)
                    if order.status() == OrderStatus.PARTIAL: self.bid_side.place(order)
                else:
                    self.bid_side.place(order)
                    result = LimitResult(True, order.id())

            case OrderSide.ASK:
                if self._is_market(order):
                    result = engine.execute(order, self.bid_side)
                    if order.status() == OrderStatus.PARTIAL: self.ask_side.place(order)
                else:
                    self.ask_side.place(order)
                    result = LimitResult(True, order.id())

        if result.success(): self.id2order[order.id()] = order

        if order.status() == OrderStatus.PARTIAL:
            msg = f"<orderbook>: order partially filled by engine, {order.quantity()} " f"placed at {order.price()}"
            result.add_message(msg)

        return result

    def _is_market(self, order: Order) -> bool:
        '''Check if an order is a market order.'''
        match order.side():
            case OrderSide.BID:
                if self.ask_side.empty(): return False
                if self.best_ask() <= order.price(): return True

            case OrderSide.ASK:
                if self.bid_side.empty(): return False
                if self.best_bid() >= order.price(): return True

        return False

    def __repr__(self) -> str:
        '''Outputs the order-book in the following format:\n

        Order-book <pair>:
        - ...
        - AskLimit(price=.., size=.., vol=..)
        -------------------------------------
        - BidLimit(price=.., size=.., vol=..)
        - ...
        '''
        length = 48
        buffer = io.StringIO()
        buffer.write(" " * (length // 2 - 9) + f"ORDER-BOOK {self.name}\n")
        buffer.write(colored(str(self.ask_side), "red"))
        buffer.write(" " + ("-" * length) + "\n")
        buffer.write(colored(str(self.bid_side), "green"))

        if self.ask_side.empty() or self.bid_side.empty(): return buffer.getvalue()

        buffer.write(colored(f"\n    Spread = {self.spread()}", color="blue"))
        buffer.write(colored(f", Mid-price = {self.midprice()}\n", color="blue"))

        return buffer.getvalue()

    def display(self) -> None:
        '''Clear terminal & display order-book.'''
        os.system("cls" if os.name == "nt" else "clear"); print("\n", self, "\n")

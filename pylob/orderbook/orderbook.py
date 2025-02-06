from io import StringIO
from typing import Optional, Iterable
from decimal import Decimal

from pylob import engine
from pylob.enums import OrderSide
from pylob.engine import EngineResult
from pylob.side import AskSide, BidSide
from pylob.limit import Limit
from pylob.order import OrderParams, Order, AskOrder, BidOrder

class OrderBook:
    '''
    The `OrderBook` is a collection of bid and ask limits. The OB is reponsible 
    for calling the matching engine functions, but not safety checking. 
    '''
    name     : str
    ask_side : AskSide
    bid_side : BidSide

    def __init__(self, name : Optional[str] = None):
        '''
        Args:
            pair (Optional[str]): A name for the order-book. Defaults to None.
        '''
        self.name     = name if name else ''
        self.ask_side = AskSide()
        self.bid_side = BidSide()

    def process_one(self, order_params : OrderParams) -> EngineResult:
        '''Creates and processes the order corresponding to the corresponding
        arguments.

        Args:
            order_params (OrderParams): Parameters of order to create.

        Returns:
            EngineResult: The result of processing the order params.
        '''
        order : Order = None # create the proper order
        match order_params.side:
            case OrderSide.BID: order = BidOrder(order_params)
            case OrderSide.ASK: order = AskOrder(order_params)

        return self.process_order(order)

    def process_many(self, orders_params : Iterable[OrderParams]) -> list[EngineResult]:
        '''Process many orders at once.

        Args:
            orders (Iterable[Order]): Orders to process.
        '''
        return [self.process_one(orderp) for orderp in orders_params]

    def process_order(self, order : Order) -> EngineResult:
        '''Place or execute the given order depending on its price level.

        Args:
            order (Order): The order to process.

        Raises:
            ValueError: If the order side is undefined.

        Returns:
            ExecutionResult: The result of the matching engine.
        '''
        match order.side():
            case OrderSide.BID: 
                if self.is_market(order):
                    return engine.execute(order, self.ask_side)
                else: return engine.place(order, self.bid_side)

            case OrderSide.ASK:
                if self.is_market(order):
                    return engine.execute(order, self.bid_side)
                else: return engine.place(order, self.ask_side)

    def is_market(self, order : Order) -> bool:
        '''Check if an order is a market order.

        Args:
            order (Order): The order to check.

        Raises:
            ValueError: If the order side is undefined.

        Returns:
            bool: True if the order is a market order false otherwise.
        '''
        match order.side():
            case OrderSide.BID: 
                if self.ask_side.empty(): return False
                if self.best_ask().price() <= order.price(): return True
            case OrderSide.ASK:
                if self.bid_side.empty(): return False
                if self.best_bid().price() >= order.price(): return True
        return False

    def best_ask(self) -> Limit: 
        '''Get the best ask limit in the book.

        Returns:
            Limit: The best ask limit.
        '''
        return self.ask_side.best()

    def best_bid(self) -> Limit: 
        '''Get the best bid limit in the book.

        Returns:
            Limit: The best bid limit.
        '''
        return self.bid_side.best()

    def bids_count(self) -> int:
        '''Get the number of bids limits in the book.

        Returns:
            int: The number of bids limits.
        '''
        return self.bid_side.size()

    def asks_count(self) -> int:
        '''Get the number of asks limits in the book.

        Returns:
            int: The number of asks limits.
        '''
        return self.ask_side.size()

    def prices_count(self) -> int:   
        '''Get the total number of limits (price levels) in the book.

        Returns:
            int: Number of limits.
        '''
        return self.asks_count() + self.bids_count()
 
    def midprice(self) -> Decimal:
        '''Get the order-book mid-price.

        Returns:
            Decimal: (best_bid + best_ask) / 2
        '''
        best_ask, best_bid = self.best_ask().price(), self.best_bid().price()
        return Decimal(0.5) * (best_ask + best_bid)

    def spread(self) -> Decimal:
        '''Get the order-book spread.

        Returns:
            Decimal: best_ask - best_bid
        '''
        return self.best_ask().price() - self.best_bid().price()

    def __repr__(self):
        '''Outputs the order-book in the following format:\n

        Order-book <pair>:
        - ...
        - AskLimit(price=.., size=.., vol=..)
        -------------------------------------
        - BidLimit(price=.., size=.., vol=..)
        - ...

        '''
        buffer = StringIO()
        buffer.write(f'\nOrder-book {self.name}:\n')
        length = 50
        buffer.write(str(self.ask_side))
        buffer.write(' ' + ('-' * length) + '\n')
        buffer.write(str(self.bid_side))
        return buffer.getvalue()
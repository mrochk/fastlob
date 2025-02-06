from io import StringIO
from typing import Optional, Iterable
from dataclasses import dataclass
from decimal import Decimal

from pylob import engine, OrderSide, OrderType, todecimal
from pylob.engine import EngineResult
from pylob.side import AskSide, BidSide
from pylob.limit import Limit
from pylob.order import Order, AskOrder, BidOrder
from pylob.consts import num

@dataclass(repr=True)
class OrderParams:
    side     : OrderSide
    price    : Decimal
    quantity : Decimal
    type     : OrderType = OrderType.GTC
    expiry   : Optional[float] = None

    def __init__(self, side : OrderSide, price : num, quantity : num,
                 type : OrderType = OrderType.GTC, 
                 expiry : Optional[float] = None):

        if not isinstance(side, OrderSide): raise TypeError()
        if not isinstance(price, num)     : raise TypeError()
        if not isinstance(quantity, num)  : raise TypeError()
        if not isinstance(type, OrderType): raise TypeError()
        if not isinstance(expiry, float)  : raise TypeError()

        if price <= 0: 
            raise ValueError(f'price ({price}) must be strictly positive')

        if quantity <= 0: 
            raise ValueError(f'quantity ({quantity}) must be strictly positive')

        self.side     = side
        self.price    = todecimal(price)
        self.quantity = todecimal(quantity)
        self.type     = type
        self.expiry   = expiry

    def unwrap(self) -> tuple[Decimal, Decimal, OrderType, float]:
        return (self.price, self.quantity, self.type, self.expiry)

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
            case OrderSide.BID: order = BidOrder(*order_params.unwrap())
            case OrderSide.ASK: order = AskOrder(*order_params.unwrap())

        return self.process_order(order)

    def process_many(self, orders_params : Iterable[OrderParams]) -> list[EngineResult]:
        '''Process many orders at once.

        Args:
            orders (Iterable[Order]): Orders to process.
        '''
        return [self.process_one(orderp) for orderp in orders_params]

    def process_order(self, order : Order) -> EngineResult:
        '''Place or execute the given order.

        Args:
            order (Order): The order to process.

        Raises:
            ValueError: If the order side is undefined.

        Returns:
            ExecutionResult: _
        '''
        match order.side():
            case OrderSide.BID: 
                if self.is_market(order):
                    return engine.execute(order, self.ask_side)
                # else, is limit order
                else: return engine.place(order, self.bid_side)

            case OrderSide.ASK:
                if self.is_market(order):
                    return engine.execute(order, self.bid_side)
                # else, is limit order
                else: return engine.place(order, self.ask_side)

    def is_market(self, order : Order) -> bool:
        '''Check if an order is a market order.

        Args:
            order (Order): The order to check.

        Raises:
            ValueError: If the order side is undefined.

        Returns:
            bool: True if the order is a market order False otherwise.
        '''
        match order.side():
            case OrderSide.BID: return self._is_market_bid(order)
            case OrderSide.ASK: return self._is_market_ask(order)

    def _is_market_bid(self, order : Order):
        assert order.side() == OrderSide.BID

        if self.asks_count() == 0: return False
        lim = self.best_ask()

        return order.price() >= lim.price()

    def _is_market_ask(self, order : Order):
        assert order.side() == OrderSide.ASK

        if self.bids_count() == 0: return False
        lim = self.best_bid()

        return order.price() <= lim.price()

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
        mkline = lambda lim: ' - ' + str(lim) + '\n'

        buffer = StringIO()
        
        buffer.write(f'\nOrder-book {self.name}:\n')

        length = 50

        ask_size = self.ask_side.size()
        bid_size = self.bid_side.size()

        ten_asks = list()
        i = 0
        for asklim in self.ask_side.limits():
            if i > 10: break
            i += 1
            ten_asks.append(asklim)

        if ask_size > 10: buffer.write(f'...({ask_size - 10} more asks)\n')

        for asklim in reversed(ten_asks):
            length = buffer.write(mkline(asklim)) - 2

        buffer.write(' ' + ('-' * length) + '\n')

        i = 0
        for bidlim in self.bid_side.limits(): 
            if i > 10: 
                if i < bid_size: buffer.write(f'...({bid_size - 10} more bids)\n')
                break
            i += 1
            buffer.write(mkline(bidlim))
            

        return buffer.getvalue()
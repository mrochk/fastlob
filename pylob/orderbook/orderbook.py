from io import StringIO
from typing import Optional, Iterable
from dataclasses import dataclass
from decimal import Decimal

from pylob import engine, OrderSide, OrderType
from pylob.engine import ExecutionResult
from pylob.side import AskSide, BidSide
from pylob.limit import Limit
from pylob.order import Order, AskOrder, BidOrder
from pylob.consts import num

@dataclass(init=True, repr=True)
class OrderParams:
    price    : num
    quantity : num
    side     : OrderSide
    type     : OrderType = OrderType.GTC
    expiry   : Optional[float] = None

    def unwrap(self) -> tuple:
        return (
            self.price, 
            self.quantity,
            self.side,
            self.type,
            self.expiry
        )

class OrderBook:
    '''
    The `OrderBook` is a collection of bid and ask limits. The OB is reponsible 
    for safety checking as well as calling the proper matching engine functions. 
    '''
    ask_side : AskSide
    bid_side : BidSide
    name     : str

    def __init__(self, name : Optional[str] = None):
        '''
        Args:
            pair (Optional[str]): A name for the order-book. Defaults to None.
        '''
        self.name     = name if name else ''
        self.ask_side = AskSide()
        self.bid_side = BidSide()

    def process_one(self, order_params : OrderParams) -> ExecutionResult:
        '''Creates and processes the order corresponding to the corresponding
        arguments. 

        Args:
            price (num): The price at which the order should be sitting/be 
            executed.
            quantity (num): The quantity to buy/sell.
            side (OrderSide): The side of the order.
            type (OrderType): The type of order to create. Defaults to GTC.
            expiry (float): The expiry timestamp of the order. Defaults to None.

        Raises:
            ValueError: If incorrect side value is passed.
        '''

        price, quantity, side, type, expiry = order_params.unwrap()

        if price <= 0: raise ValueError(f'invalid order price ({price})')
        if quantity <= 0: raise ValueError(f'invalid order qty ({quantity})')

        order : Optional[Order] = None # create the proper order
        match side:
            case OrderSide.BID: order = BidOrder(price, quantity, type, expiry)
            case OrderSide.ASK: order = AskOrder(price, quantity, type, expiry)
            case _: raise ValueError('undefined side')

        return self.process_order(order)

    def process_order(self, order : Order) -> ExecutionResult:
        '''Place or execute the given order.

        Args:
            order (Order): The order to process.

        Raises:
            ValueError: If the order side is undefined.

        Returns:
            _: _
        '''
        operation = None # the operation to execute

        match order.side():
            case OrderSide.BID: 
                if self.is_market(order):
                    # sanity check market
                    operation = lambda: engine.execute(order, self.ask_side)
                # else, is limit order
                else: operation = lambda: engine.place(order, self.bid_side)

            case OrderSide.ASK:
                if self.is_market(order):
                    # sanity check market
                    operation = lambda: engine.execute(order, self.bid_side)
                # else, is limit order
                else: operation = lambda: engine.place(order, self.ask_side)

            case _: raise ValueError('undefined side')

        # execute operation
        return operation()

    def process_many(self, orders_params : Iterable[OrderParams]) -> list[ExecutionResult]:
        '''Process many orders at once.

        Args:
            orders (Iterable[Order]): Orders to process.
        '''
        return [self.process_one(orderp) for orderp in orders_params]

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
            case _: raise ValueError('undefined side')

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
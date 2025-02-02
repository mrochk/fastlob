import io
from sortedcollections import SortedDict
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from pylob.engine import MatchingEngine
from pylob.side import AskSide, BidSide
from pylob.limit import Limit
from pylob.order import *
from pylob.consts import num

@dataclass(repr=True)
class Result:
    def __init__(self, success : bool, order_id : int, 
                 message : Optional[str]):
        self.success  = success
        self.order_id = order_id
        self.message  = message

class UndefinedSide(Exception): pass

class UndefinedType(Exception): pass

class OrderBook:
    '''
    The order-book is a collection of bid and ask limits, with a matching
    engine that handles all the logic related to executing orders.
    The OB is reponsible to safety checking as well as calling the correct
    methods. 
    '''
    engine   : MatchingEngine
    ask_side : AskSide
    bid_side : BidSide
    pair     : str

    def __init__(self, pair : Optional[str] = None):
        self.pair     = pair if pair else ''
        self.ask_side = AskSide()
        self.bid_side = BidSide()
        self.engine   = MatchingEngine()

    def process(self, 
                price    : num, 
                quantity : num, 
                side     : OrderSide, 
                type     : OrderType = OrderType.GTC, 
                expiry   : float = None,
                ) -> Result:

        order = None
        match side:
            case OrderSide.BID: order = BidOrder(price, quantity, type, expiry)
            case OrderSide.ASK: order = AskOrder(price, quantity, type, expiry)
            case _: raise UndefinedSide
        return self.process_order(order)

    def process_order(self, order : Order) -> Result:
        match order.side():
            case OrderSide.BID: 
                if self.is_market(order):
                    # sanity check market
                    self.engine.execute(order, self.bid_side)
                    return None
                # else, is limit order
                self.engine.place(order, self.bid_side)

            case OrderSide.ASK:
                if self.is_market(order):
                    # sanity check market
                    self.engine.execute(order, self.bid_side)
                    return None
                # else, is limit order
                self.engine.place(order, self.ask_side)

            case _: return Result(False, order.id(), 'undefined side')

    def is_market(self, order : Order) -> bool:
        match order.side():
            case OrderSide.BID: return self._is_market_bid(order)
            case OrderSide.ASK: return self._is_market_ask(order)
            case _: raise UndefinedSide

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

    def best_ask(self) -> Limit: return self.ask_side.best()

    def best_bid(self) -> Limit: return self.bid_side.best()

    def bids_count(self) -> int: return self.bid_side.size()

    def asks_count(self) -> int: return self.ask_side.size()

    def prices_count(self) -> int: 
        return self.asks_count() + self.bids_count()
 
    def midprice(self) -> Decimal:
        '''
        midprice = (best_ask + best_bid) / 2
        '''
        bestasklim = self.best_ask()
        bestbidlim = self.best_bid()
        return Decimal(0.5) * (bestbidlim.__price + bestasklim.__price)

    def spread(self) -> Decimal:
        '''
        spread = best_ask - best_bid
        '''
        bestask, _ = self.ask_side.peekitem(0)
        bestbid, _ = self.bid_side.peekitem(0)
        return bestask - bestbid

    def __repr__(self):
        '''
        Outputs the order-book in the following format:\n
        Order-book <pair>:
        - ...
        - (Ask)Limit(price=.., size=.., vol=..)
        -----------------------------------------
        - (Bid)Limit(price=.., size=.., vol=..)
        - ...
        '''
        mkline = lambda lim: ' - ' + str(lim) + '\n'

        buffer = io.StringIO()
        
        buffer.write(f'Order-book {self.pair}:\n')

        length = 50

        for asklim in reversed(self.ask_side.values()):
            length = buffer.write(mkline(asklim)) - 2

        buffer.write(' ' + ('-' * length) + '\n')

        for bidlim in self.bid_side.values(): buffer.write(mkline(bidlim))

        return buffer.getvalue()
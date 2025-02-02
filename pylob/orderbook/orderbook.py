import io
from sortedcollections import SortedDict
from typing import Optional
from decimal import Decimal

from pylob.order import *
from pylob.limit import Limit
from pylob.consts import num

class UndefinedSide(Exception): pass

class UndefinedType(Exception): pass

class OrderBook:
    asks : SortedDict
    bids : SortedDict
    pair : str

    def __init__(self, pair : Optional[str] = None):
        self.asks = SortedDict()
        self.bids = SortedDict(lambda x: -x)
        self.pair = pair if pair else ''

    def process(self, price : num, quantity : num, side : OrderSide, 
                    type : OrderType = OrderType.GTC) -> Optional[int]:
        match side:
            case OrderSide.BID: 
                order = BidOrder(price, quantity, type)
                return self.process_order(order)
            case OrderSide.ASK:
                order = AskOrder(price, quantity, type)
                return self.process_order(order)
            case _: raise UndefinedSide

    def process_order(self, order : Order) -> Optional[int]:
        match order.side:
            case OrderSide.BID: 
                if self.is_market(order) and self.execute_bid_order(order):
                    return order.identifier
                if self.place_bid_order(order): return order.identifier
            case OrderSide.ASK:
                if self.is_market(order) and self.execute_ask_order(order):
                    return order.identifier
                if self.place_ask_order(order): return order.identifier
            case _: raise UndefinedSide

    def is_market(self, order : Order) -> bool:
        match order.side:
            case OrderSide.BID: 
                if self.total_asks_lim() == 0: return False
                lim = self.best_ask()
                return order.price >= lim.price
            case OrderSide.ASK:
                if self.total_bids_lim() == 0: return False
                lim = self.best_bid()
                return order.price <= lim.price
            case _: raise UndefinedSide

    def place_ask_order(self, order : AskOrder) -> bool:
        if order.type == OrderType.FOK: return False

        # if price exists
        if order.price in self.asks.keys():
            limit = self.asks[order.price]
            return limit.add_order(order)

        # if price doesnt exist create limit
        limit = Limit(order.price)
        if not limit.add_order(order): return False 
        self.asks[order.price] = limit
        return True

    def place_bid_order(self, order : BidOrder) -> bool:
        if order.type == OrderType.FOK: return False

        # if price exists
        if order.price in self.bids.keys():
            limit = self.bids[order.price]
            return limit.add_order(order)

        # if price doesnt exist create limit
        limit = Limit(order.price)
        if not limit.add_order(order): return False 
        self.bids[order.price] = limit
        return True

    def execute_ask_order(self, order : AskOrder) -> bool:
        best_bid_limit = self.best_bid()
        assert order.price <= best_bid_limit.price

        match order.type:
            case OrderType.FOK: 
                if OrderBook.can_exec_FOK(order, best_bid_limit):
                    best_bid_limit.execute(order)
            case OrderType.GTC: raise NotImplemented
            case OrderType.GTD: raise NotImplemented
            case _: raise UndefinedType

        if best_bid_limit.volume == 0:
            del self.bids[best_bid_limit.price]

    @staticmethod
    def can_exec_FOK(order : Order, limit : Limit):
        assert order.type == OrderType.FOK
        assert order.price == limit.price
        return limit.volume >= order.quantity

    def best_ask(self) -> Limit: 
        _, lim = self.asks.peekitem(0); return lim

    def best_bid(self) -> Limit: 
        _, lim = self.bids.peekitem(0); return lim 

    def total_bids_lim(self): return len(self.bids)

    def total_asks_lim(self): return len(self.asks)

    def total_lim(self): return self.total_asks_lim() + self.total_bids_lim()

    def midprice(self):
        '''
        midprice = (best_ask + best_bid) / 2
        '''
        bestasklim = self.best_ask()
        bestbidlim = self.best_bid()
        return Decimal(0.5) * (bestbidlim.price + bestasklim.price)

    def spread(self):
        '''
        spread = best_ask - best_bid
        '''
        bestask, _ = self.asks.peekitem(0)
        bestbid, _ = self.bids.peekitem(0)
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

        for asklim in reversed(self.asks.values()):
            length = buffer.write(mkline(asklim)) - 2

        buffer.write(' ' + ('-' * length) + '\n')

        for bidlim in self.bids.values(): buffer.write(mkline(bidlim))

        return buffer.getvalue()
from sortedcollections import SortedDict
from typing import Optional
from decimal import Decimal

from pylob.order import *
from pylob.limit import Limit
from pylob.consts import num

class OrderBook:
    asks : SortedDict
    bids : SortedDict

    def __init__(self):
        self.asks = SortedDict()
        self.bids = SortedDict(lambda x: -x)

    def place_order(self, price : num, quantity : num, side : OrderSide, 
                    type : OrderType = OrderType.FOK) -> Optional[int]:
        match side:

            case OrderSide.BID: 
                order = BidOrder(price, quantity, type)
                if self.place_bid_order(order): return order.identifier

            case OrderSide.ASK:
                order = AskOrder(price, quantity, type)
                if self.place_ask_order(order): return order.identifier

            case _: raise Exception

    def place_ask_order(self, order : AskOrder) -> bool:
        # if price exists
        if order.price in self.asks.keys():
            limit = self.asks[order.price]
            return limit.add_order(order)

        # if price doesnt exists create limit
        limit = Limit(order.price)
        if not limit.add_order(order): return False 
        self.asks[order.price] = limit
        return True

    def place_bid_order(self, order : BidOrder) -> bool:
        # if price exists
        if order.price in self.bids.keys():
            limit = self.bids[order.price]
            return limit.add_order(order)

        # if price doesnt exists create limit
        limit = Limit(order.price)
        if not limit.add_order(order): return False 
        self.bids[order.price] = limit
        return True

    def n_bids_limits(self): return len(self.bids)

    def n_asks_limits(self): return len(self.asks)

    def n_limits(self): return self.n_asks_limits() + self.n_bids_limits()

    def midprice(self):
        bestask, _ = self.asks.peekitem(0)
        bestbid, _ = self.bids.peekitem(0)
        return Decimal(0.5) * (bestbid + bestask)

    def spread(self):
        bestask, _ = self.asks.peekitem(0)
        bestbid, _ = self.bids.peekitem(0)
        return bestask - bestbid

    def display(self) -> None:
        print()
        for asklimit in reversed(self.asks.values()):
            print(asklimit)
        print('_____________________')
        for bidlimit in self.bids.values():
            print(bidlimit)
        print()
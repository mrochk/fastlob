import logging
from decimal import Decimal
from typing import Optional

from fastlob.side import Side, AskSide, BidSide
from fastlob.limit import Limit
from fastlob.order import Order, AskOrder, BidOrder
from fastlob.result import ResultBuilder
from fastlob.enums import OrderType
from fastlob.utils import zero

def not_running_error(logger: logging.Logger) -> ResultBuilder:
    result = ResultBuilder.new_error()
    errmsg = 'lob is not running (<ob.start> must be called before it can be used)'
    result.add_message(errmsg); logger.error(errmsg)
    return result

def best_limits(n: int, side: Side) -> list[tuple[Decimal, Decimal, int]]:
    result = list()

    for i, lim in enumerate(side.limits()):
        if i >= n: break
        t = (lim.price(), lim.volume(), lim.valid_orders())
        result.append(t)

    return result

def is_market_ask(bid_side : BidSide, order: AskOrder) -> bool:
    if bid_side.empty(): return False
    if bid_side.best().price() >= order.price(): return True
    return False

def is_market_bid(ask_side : AskSide, order: BidOrder) -> bool:
    if ask_side.empty(): return False
    if ask_side.best().price() <= order.price(): return True
    return False

def check_limit_order(order: Order) -> Optional[str]:
    match order.otype():
        case OrderType.FOK: # FOK order can not be a limit order by definition
            return 'FOK order is not immediately matchable'
    return None

def check_bid_market_order(ask_side: AskSide, order: BidOrder) -> Optional[str]:
    match order.otype():
        case OrderType.FOK: # check that order quantity can be filled
            if not immediately_matchable_bid(ask_side, order):
                return 'FOK bid order is not immediately matchable'
    return None

def check_ask_market_order(bid_side: BidSide, order: AskOrder) -> Optional[str]:
    match order.otype():
        case OrderType.FOK: # check that order quantity can be filled
            if not immediately_matchable_ask(bid_side, order):
                return 'FOK ask order is not immediately matchable'
    return None

def immediately_matchable_bid(ask_side: AskSide, order: BidOrder) -> bool:
    # we want the limit volume down to the order price to be >= order quantity
    volume = zero()
    limits = ask_side.limits()

    lim : Limit
    for lim in limits:
        if lim.price() > order.price(): break
        if volume >= order.quantity(): break
        volume += lim.volume()

    if volume < order.quantity(): return False
    return True

def immediately_matchable_ask(bid_side: BidSide, order: AskOrder) -> bool:
    # we want the limit volume down to the order price to be >= order quantity
    volume = zero()
    limits = bid_side.limits()

    lim : Limit
    for lim in limits:
        if lim.price() < order.price(): break
        if volume >= order.quantity(): break
        volume += lim.volume()

    if volume < order.quantity(): return False
    return True
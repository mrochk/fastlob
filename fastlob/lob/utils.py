import logging
from typing import Optional
from numbers import Number

from fastlob.order import Order
from fastlob.result import ResultBuilder
from fastlob.enums import OrderType

# mostly safety checking

def not_running_error(logger: logging.Logger) -> ResultBuilder:
    result = ResultBuilder.new_error()
    errmsg = 'lob is not running (<ob.start> must be called before it can be used)'
    result.add_message(errmsg); logger.error(errmsg)
    return result

def check_limit_order(order: Order) -> Optional[str]:
    match order.otype():
        case OrderType.FOK: # FOK order can not be a limit order by definition
            return 'FOK order is not immediately matchable'
    return None

def check_update_pair(pair):
    if not isinstance(pair, tuple) or len(pair) != 2:
        raise ValueError('must be pairs of (price, volume)')

    price, volume = pair

    if not isinstance(price, Number) or not isinstance(volume, Number):
        raise ValueError('(price, volume) must be both instances of Number')

    if price <= 0: raise ValueError(f'price must be strictly positive but is {price}')

def check_snapshot_pair(pair):
    check_update_pair(pair)

    _, volume = pair
    if volume <= 0: raise ValueError(f'volume must be strictly positive but is {volume}')
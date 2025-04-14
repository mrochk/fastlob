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
'''Utility functions for lob.'''

import logging
from typing import Optional

from fastlob.order import Order
from fastlob.result import ResultBuilder
from fastlob.enums import OrderType

# mostly safety checking

def not_running_error(logger: logging.Logger) -> ResultBuilder:
    '''Build the *not running error*.'''

    result = ResultBuilder.new_error()
    errmsg = 'lob is not running (<ob.start> must be called before it can be used)'
    result.add_message(errmsg); logger.error(errmsg)
    return result

def check_limit_order(order: Order) -> Optional[str]:
    '''Check if limit order can be processed.'''

    match order.otype():

        case OrderType.FOK: # FOK order can not be a limit order by definition
            return 'FOK order is not immediately matchable'

    return None

'''
The matching engine module, could also be a static class.
'''

from dataclasses import dataclass
from enum import Enum
from abc import ABC
from typing import Optional
from decimal import Decimal

from pylob import OrderType
from pylob.limit import Limit
from pylob.side import Side
from pylob.order import Order

@dataclass(repr=True)
class EngineResult(ABC):
    success    : bool
    identifier : Optional[int]
    message    : Optional[str]

    def __init__(self, success, identifier, message=None):
        self.identifier = identifier if success else None 
        self.success = success
        self.message = message

@dataclass(init=True, repr=True)
class PlaceResult(EngineResult):
    pass

@dataclass(init=True, repr=True)
class ExecResult(EngineResult):
    orders_matched   : int
    limits_matched   : int
    execution_prices : dict[Decimal, Decimal]

def place(order : Order, side : Side) -> PlaceResult:
    '''Place a limit order.

    Args:
        order (Order): The order to place.
        side (Side): The side at which the order should be place.
    '''
    success = True 
    message = None

    try:
        if not side.limit_exists(order.price()): side.add_limit(order.price())
        side.add_order(order)

    except ValueError as e:
        success = False
        message = str(e)

    return PlaceResult(
        success=success,
        identifier=order.id(),
        message=message,
    )

def add_dict(dictionary : dict, key : Decimal, value : Decimal):
    if value in dictionary: dictionary[key] += value
    else: dictionary[key] = value

def execute(order : Order, side : Side) -> ExecResult:
    '''Execute a market order.

    Args:
        order (Order): The order to execute.
        side (Side): The side at which the order should be executed.
    '''
    if order.quantity() > side.volume():
        return ExecResult(
            success=False,
            identifier=None,
            message=f'order quantity bigger than side volume ({order.quantity()} > {side.volume()})',
            limits_matched=0,
            orders_matched=0,
            execution_prices=None
        )

    execution_prices = dict()
    limits_matched = orders_matched = 0
    
    lim = side.best()

    while order.quantity() >= lim.volume():
        limits_matched += 1
        orders_matched += lim.size()

        execution_prices[lim.price()] = lim.volume()

        order.partial_fill(lim.volume())
        side.remove_limit(lim.price())
        
        lim = side.best()

    lim_order = lim.next_order()

    while order.quantity() > lim_order.quantity():
        orders_matched += 1

        add_dict(execution_prices, lim.price(), lim_order.quantity())

        order.partial_fill(lim_order.quantity())
        lim.pop_next_order()
        lim_order = lim.next_order()

    add_dict(execution_prices, lim.price(), order.quantity())
    lim.partial_fill(lim_order.id(), order.quantity())

    return ExecResult(
        success=True,
        identifier=order.id(),
        orders_matched=orders_matched,
        limits_matched=limits_matched,
        execution_prices=execution_prices,
        message=None,
    )
from decimal import Decimal

from pylob.side import Side
from pylob.order import Order, OrderStatus

from .result import PlaceResult, ExecResult 

def place(order : Order, side : Side) -> PlaceResult:
    '''Place a limit order.

    Args:
        order (Order): The order to place.
        side (Side): The side at which the order should be placed.
    '''
    success, message = True, "" 

    try:
        side.add_limit_if_not_exists(order.price())
        side.add_order(order)

    except ValueError as e:
        success = False
        message = str(e)

    return PlaceResult(
        success=success,
        identifier=order.id() if success else 0,
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
        message = f'order quantity bigger than side volume '+ \
                  f'({order.quantity()} > {side.volume()})'
        return ExecResult(success=False, message=message)

    execution_prices = dict()
    limits_matched = orders_matched = 0
    
    while order.quantity() > 0:
        lim = side.best()

        if order.quantity() < lim.volume(): break

        limits_matched += 1
        orders_matched += lim.size()
        execution_prices[lim.price()] = lim.volume()

        order.fill(lim.volume())
        side.fill_best()

    while order.quantity() > 0:
        lim_order = side.best().next_order()

        if order.quantity() < lim_order.quantity(): break

        orders_matched += 1
        add_dict(execution_prices, lim_order.price(), lim_order.quantity())

        lim_order.fill(order.quantity())
        order.fill(lim_order.quantity())

        lim_order = lim.pop_next_order()

    if order.quantity() > 0:
        add_dict(execution_prices, lim.price(), order.quantity())

        side.best().partial_fill(lim_order.id(), order.quantity())
        order.fill(order.quantity())

    return ExecResult(
        success=True,
        identifier=order.id(),
        orders_matched=orders_matched,
        limits_matched=limits_matched,
        execution_prices=execution_prices,
    )
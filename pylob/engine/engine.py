from decimal import Decimal
from collections import defaultdict

from pylob.side import Side
from pylob.order import Order
from pylob.consts import ZERO

from .result import PlaceResult, ExecResult 

def place(order : Order, side : Side) -> PlaceResult:
    '''Place a limit order.

    Args:
        order (Order): The order to place.
        side (Side): The side at which the order should be placed.
    '''
    price = order.price()

    if not side.price_exists(price): side.add_limit(price)
    side.get_limit(price).add_order(order)

    return PlaceResult(success=True, identifier=order.id())

def execute(order : Order, side : Side) -> ExecResult:
    '''Execute a market order.

    Args:
        order (Order): The order to execute.
        side (Side): The side at which the order should be executed.
    '''
    if order.quantity() > side.volume():
        return ExecResult(
            success=False, 
            message=f'order quantity bigger than side volume '+ \
                f'({order.quantity()} > {side.volume()})'
        )

    limits_matched = orders_matched = 0
    execprices = defaultdict(lambda: ZERO)
    
    while order.quantity() > 0:
        lim = side.best()

        if order.quantity() < lim.volume(): break

        limits_matched += 1
        orders_matched += lim.size()
        execprices[lim.price()] = lim.volume()

        order.fill(lim.volume())
        side.fill_best()

    while order.quantity() > 0:
        lim_order = side.best().next_order()

        if order.quantity() < lim_order.quantity(): break

        orders_matched += 1
        execprices[lim_order.price()] += lim_order.quantity()

        lim_order.fill(order.quantity())
        order.fill(lim_order.quantity())

        lim_order = lim.pop_next_order()

    if order.quantity() > 0:
        execprices[lim_order.price()] += order.quantity()

        side.best().partial_fill_next(order.quantity())
        order.fill(order.quantity())

    return ExecResult(
        success=True,
        identifier=order.id(),
        orders_matched=orders_matched,
        limits_matched=limits_matched,
        execution_prices=execprices,
    )
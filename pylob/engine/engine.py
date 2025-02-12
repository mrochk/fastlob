"""The engine module is only responsible for executing market orders."""

from decimal import Decimal

from pylob.enums import OrderSide, OrderStatus
from pylob.side import Side
from pylob.order import Order
from pylob.orderbook.result import MarketResult

def execute(order: Order, side: Side) -> MarketResult:
    """Execute a market order.

    Args:
        order (Order): The order to execute.
        side (Side): The side at which the order should be matched.
    """
    result = MarketResult(success=False)

    out_of_price = _fill_whole_limits(side, order, result)
    if out_of_price: return _result_okay(result, order.id())

    out_of_price = _fill_whole_orders(side, order, result)
    if out_of_price: return _result_okay(result, order.id())

    _fill_partial_order(side, order, result)

    return _result_okay(result, order.id())

def _fill_whole_limits(side: Side, order: Order, result: MarketResult) -> bool:
    """While the order to execute is larger than entire limits."""
    while order.quantity() > 0 and not side.empty():
        lim = side.best()

        if _out_of_price(order, lim.price()):
            msg = f"<engine>: order out of price at ({lim.price()}), quantity left: ({order.quantity()})"
            result.add_message(msg)
            return True

        if order.quantity() < lim.volume(): return False

        result.limits_matched += 1
        result.orders_matched += lim.valid_orders()
        result.execution_prices[lim.price()] = lim.volume()

        order.fill(lim.volume())
        side._volume -= lim.volume()
        side._limits.pop(lim.price())

def _fill_whole_orders(side: Side, order: Order, result: MarketResult) -> bool:
    """While the order to execute is larger than whole orders."""
    lim = side.best()
    current_price = lim.price()

    if _out_of_price(order, current_price):
        result.add_message(f"<engine>: order out of price at {current_price}, partially filled")
        return True

    while order.quantity() > 0:
        next_order = lim.next_order()

        if order.quantity() < next_order.quantity(): return True

        result.orders_matched += 1
        result.execution_prices[next_order.price()] += next_order.quantity()

        order.fill(next_order.quantity())
        side._volume -= next_order.quantity()
        lim.pop_next_order()

def _fill_partial_order(side: Side, order: Order, result: MarketResult):
    """Partially fill the last order left with what's left of our order."""
    lim = side.best()
    lim_order = lim.next_order()
    if order.status() == OrderStatus.PARTIAL:
        result.execution_prices[lim_order.price()] += order.quantity()
        lim.fill_next(order.quantity())
        side._volume -= order.quantity()
        order.fill(order.quantity())

def _result_okay(result : MarketResult, order_id : str):
    result._success = True
    result._order_id = order_id
    return result

def _out_of_price(order: Order, lim_price: Decimal) -> bool:
    match order.side():
        case OrderSide.BID: return order.price() < lim_price
        case OrderSide.ASK: return order.price() > lim_price
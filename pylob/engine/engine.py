'''The engine module is solely responsible for executing market orders.
'''

from pylob.side import Side
from pylob.order import Order
from pylob.orderbook.result import MarketResult


def execute(order: Order, side: Side) -> MarketResult:
    '''Execute a market order.

    Args:
        order (Order): The order to execute.
        side (Side): The side at which the order should be executed.
    '''
    result = MarketResult(success=False)

    if order.quantity() > side.volume():
        result._message = f'order quantity bigger than side volume ' + \
            f'({order.quantity()} > {side.volume()})'
        return result

    _fill_whole_limits(side, order, result)
    _fill_whole_orders(side, order, result)
    _fill_partial_order(side, order, result)

    result._success = True
    result._identifier = order.id()
    return result


def _fill_whole_limits(side: Side, order: Order, result: MarketResult):
    '''While the order to execute is larger than entire limits.
    '''
    while order.quantity() > 0:
        lim = side.best()

        if order.quantity() < lim.volume():
            break

        result.limits_matched += 1
        result.orders_matched += lim.valid_orders()
        result.execution_prices[lim.price()] = lim.volume()

        order.fill(lim.volume())
        side._volume -= lim.volume()
        side._limits.pop(lim.price())


def _fill_whole_orders(side: Side, order: Order, result: MarketResult):
    '''While the order to execute is larger than whole orders.
    '''
    while order.quantity() > 0:
        lim = side.best()
        next_order = lim.get_next_order()

        if order.quantity() < next_order.quantity():
            return

        result.orders_matched += 1
        result.execution_prices[next_order.price()] += next_order.quantity()

        order.fill(next_order.quantity())
        side._volume -= next_order.quantity()
        lim.delete_next_order()


def _fill_partial_order(side: Side, order: Order, result: MarketResult):
    '''Partially fill the last order left with our order.
    '''
    if order.quantity() > 0:
        lim_order = side.best().get_next_order()
        result.execution_prices[lim_order.price()] += order.quantity()

        side.best().partial_fill_next(order.quantity())
        side._volume -= order.quantity()
        order.fill(order.quantity())

'''The engine module is solely responsible for executing market orders.
'''

from decimal import Decimal

from pylob.enums import OrderSide
from pylob.side import Side
from pylob.order import Order
from pylob.orderbook.result import MarketResult

def _make_message(msg: str): return f'<engine>: {msg}'

def execute(order: Order, side: Side) -> MarketResult:
    '''Execute a market order.

    Args:
        order (Order): The order to execute.
        side (Side): The side at which the order should be executed.
    '''
    result = MarketResult(success=False)

    #if order.quantity() > side.volume():
        #msg = f'order quantity bigger than side volume ' + \
            #f'({order.quantity()} > {side.volume()})'
        #result.add_message(_make_message(msg))
        #return result

    continue_ = _fill_whole_limits(side, order, result)
    if not continue_: 
        result._success = True
        result._order_id = order.id()
        return result

    continue_ = _fill_whole_orders(side, order, result)
    if not continue_: 
        result._success = True
        result._order_id = order.id()
        return result

    _fill_partial_order(side, order, result)

    result._success = True
    result._identifier = order.id()

    return result

def out_of_price(order : Order, lim_price : Decimal) -> bool:
    match order.side():
        case OrderSide.BID: return order.price() < lim_price
        case OrderSide.ASK: return order.price() > lim_price

def _fill_whole_limits(side: Side, order: Order, result: MarketResult) -> bool:
    '''While the order to execute is larger than entire limits.
    '''
    while order.quantity() > 0 and not side.empty():
        lim = side.best()

        if out_of_price(order, lim.price()):
            msg = f'order out of price at ({lim.price()}), qty left ({order.quantity()})'
            result.add_message(_make_message(msg))
            return False 

        if order.quantity() < lim.volume():
            return True

        result.limits_matched += 1
        result.orders_matched += lim.valid_orders()
        result.execution_prices[lim.price()] = lim.volume()

        order.fill(lim.volume())
        side._volume -= lim.volume()
        side._limits.pop(lim.price())


def _fill_whole_orders(side: Side, order: Order, result: MarketResult) -> bool:
    '''While the order to execute is larger than whole orders.
    '''
    lim = side.best()
    current_price = lim.price()

    if out_of_price(order, current_price):
        msg = f'order out of price at {current_price}, partially filled'
        result.add_message(_make_message(msg))
        return False

    while order.quantity() > 0:
        next_order = lim.get_next_order()

        if order.quantity() < next_order.quantity():
            return True

        result.orders_matched += 1
        result.execution_prices[next_order.price()] += next_order.quantity()

        order.fill(next_order.quantity())
        side._volume -= next_order.quantity()
        lim.pop_next_order()


def _fill_partial_order(side: Side, order: Order, result: MarketResult):
    '''Partially fill the last order left with our order.
    '''
    lim = side.best()
    if order.quantity() > 0:
        lim_order = lim.get_next_order()
        result.execution_prices[lim_order.price()] += order.quantity()

        side.best().partial_fill_next(order.quantity())
        side._volume -= order.quantity()
        order.fill(order.quantity())

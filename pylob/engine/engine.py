from decimal import Decimal

from pylob.side import Side
from pylob.order import Order
from pylob.enums import OrderSide
from pylob.orderbook.result import MarketResult

'''The engine module is **only** responsible for executing market orders.'''

def execute(order: Order, side: Side) -> MarketResult:
    '''Execute a market order in a given side.'''
    result = MarketResult(success=False)

    oop = _fill_whole_limits(side, order, result)
    if oop: return _result_okay(result, order.id())

    oop = _fill_whole_orders(side, order, result)
    if oop: return _result_okay(result, order.id())

    _fill_last_order(side, order, result)
    return _result_okay(result, order.id())

def _fill_whole_limits(side: Side, order: Order, result: MarketResult) -> bool:
    '''While the order to execute is larger than entire limits, fill them.'''
    while order.quantity() > 0 and not side.empty():
        lim = side.best()

        if _oop(order, lim.price()): # if out of price break
            result.add_message(_oop_msg(lim.price(), order.quantity()))
            return True

        if order.quantity() < lim.volume(): return False # if can not match whole limits anymore, break

        # update result object
        result._limits_matched += 1
        result._orders_matched += lim.valid_orders()
        result._execution_prices[lim.price()] = lim.volume()

        order.fill(lim.volume()) # partially fill order with limit volume
        side._volume -= lim.volume() # substract limit volume from side volume before filling all orders in limit
        lim.fill_all() # set all orders to filled
        side._limits.pop(lim.price()) # remove limit from side

    return False

def _fill_whole_orders(side: Side, order: Order, result: MarketResult) -> bool:
    '''While the order to execute is larger than whole orders, fill them.'''
    if side.empty(): return False

    lim = side.best()

    if _oop(order, lim.price()):
        result.add_message(_oop_msg(lim.price(), order.quantity()))
        return True

    while order.quantity() > 0:
        next_order = lim.next_order()

        if order.quantity() < next_order.quantity(): return False

        result._orders_matched += 1
        result._execution_prices[next_order.price()] += next_order.quantity()

        order.fill(next_order.quantity())
        side._volume -= next_order.quantity()
        lim.pop_next_order()

    return False

def _fill_last_order(side: Side, order: Order, result: MarketResult):
    '''**Partially** fill the last order left with what's left of our order.'''
    if side.empty(): return

    lim = side.best()
    lim_order = lim.next_order()

    if order.valid():
        result._execution_prices[lim_order.price()] += order.quantity()

        lim.fill_next(order.quantity())
        side._volume -= order.quantity()

        order.fill(order.quantity())

def _result_okay(result : MarketResult, order_id : str):
    '''Fill result object.'''
    result._success = True; result._order_id = order_id; return result

def _oop(order: Order, lim_price: Decimal) -> bool:
    '''True if order is out of price.'''
    match order.side():
        case OrderSide.BID: return order.price() < lim_price
        case OrderSide.ASK: return order.price() > lim_price

_oop_msg = lambda p, q: f'<engine>: order out of price at ({p}), quantity left: ({q})'
'''The engine module is **only** responsible for executing market orders.'''

from decimal import Decimal

from fastlob.side import Side
from fastlob.order import Order
from fastlob.enums import OrderSide
from fastlob.result import ResultBuilder

def execute(order: Order, side: Side) -> ResultBuilder:
    '''Execute a market order at a given side.'''

    result = ResultBuilder.new_market(order.id())

    if fill_whole_limits(side, order, result):
        result.set_success(True); return result

    if fill_whole_orders(side, order, result):
        result.set_success(True); return result

    fill_last_order(side, order, result)

    result.set_success(True); return result

def fill_whole_limits(side: Side, order: Order, result: ResultBuilder) -> bool:
    '''While the order to execute is larger than entire limits, fill them.'''

    while order.quantity() > 0 and not side.empty():
        lim = side.best()

        if oop(order, lim.price()): # if out of price break
            result.add_message(mk_oop_msg(lim.price(), order.quantity()))
            return True

        if order.quantity() < lim.volume(): return False # if can not match whole limits anymore, break

        # update result object
        result.inc_orders_matched(lim.valid_orders())
        result.inc_execprices(lim.price(), lim.volume())

        order.fill(lim.volume()) # partially fill order with limit volume
        side.update_volume(-lim.volume()) # substract limit volume from side volume before filling all orders in limit
        lim.fill_all() # set all orders to filled
        side.pop_limit(lim.price()) # remove limit from side

    return False

def fill_whole_orders(side: Side, order: Order, result: ResultBuilder) -> bool:
    '''While the order to execute is larger than whole orders, fill them.'''

    if side.empty(): return False

    lim = side.best()

    if oop(order, lim.price()):
        result.add_message(mk_oop_msg(lim.price(), order.quantity()))
        return True

    while order.quantity() > 0:
        next_order = lim.next_order()

        if order.quantity() < next_order.quantity(): return False

        result.inc_orders_matched(1)
        result.inc_execprices(next_order.price(), next_order.quantity())

        order.fill(next_order.quantity())
        side.update_volume(-next_order.quantity())
        lim.pop_next_order()

    return False

def fill_last_order(side: Side, order: Order, result: ResultBuilder):
    '''**Partially** fill the last order left with what's left of our order.'''

    if side.empty(): return

    lim = side.best()
    lim_order = lim.next_order()

    if order.valid():
        result.inc_execprices(lim_order.price(), order.quantity())

        lim.fill_next(order.quantity())
        side.update_volume(-order.quantity())

        order.fill(order.quantity())

def oop(order: Order, lim_price: Decimal) -> bool:
    '''True if order is out of price.'''

    match order.side():
        case OrderSide.BID: return order.price() < lim_price
        case OrderSide.ASK: return order.price() > lim_price

def mk_oop_msg(p, q): return f'<matching engine>: order out-of-price at ({p}), quantity left: ({q})'

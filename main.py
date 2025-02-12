import time
from numpy import random
import matplotlib.pyplot as plt

import pylob
from pylob import OrderBook, OrderParams, OrderSide

def sim():
    ob = pylob.OrderBook('BTC/USDT')
    prices_over_time = list()

    for t in range(10000000):
        n_asks = random.poisson(lam=5)
        ask_prices = [pylob.todecimal(random.normal(1500, 100))
                      for _ in range(n_asks)]
        ask_qtys = [pylob.todecimal(random.normal(10, 1))
                    for _ in range(n_asks)]

        n_bids = random.poisson(lam=5)
        bid_prices = pylob.todecimal(random.normal(1500, 100, size=n_bids))
        bid_qtys = pylob.todecimal(random.normal(10, 1, size=n_bids))

        ask_orders = [pylob.OrderParams(
            pylob.OrderSide.ASK, p, q) for p, q in zip(ask_prices, ask_qtys)]
        bid_orders = [pylob.OrderParams(
            pylob.OrderSide.BID, p, q) for p, q in zip(bid_prices, bid_qtys)]
        orders = (ask_orders + bid_orders)

        random.shuffle(orders)
        results = ob.process_many(orders)

        nprices = ob.nprices()
        prices_over_time.append(nprices)

        ob.display()
        time.sleep(0.1)

if __name__ == '__main__':
    ob = OrderBook()

    r1 = ob.process_one(OrderParams(OrderSide.BID, 4111, 345))
    r2 = ob.process_one(OrderParams(OrderSide.BID, 4111, 98))

    assert r1.success()
    assert r2.success()

    id1 = r1.order_id()


    print(ob)

    print(ob.get_order_status(id1))
    print(r1)

    ob.cancel_order(id1)

    print(ob)
    print(ob.get_order_status(id1))
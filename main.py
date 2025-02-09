import time
from numpy import random

import pylob

if __name__ == '__main__':
    ob = pylob.OrderBook()

    for t in range(1000):
        n_asks = random.poisson(lam=100)
        ask_prices = [pylob.todecimal(random.normal(1500, 100))
                      for _ in range(n_asks)]
        ask_qtys = [pylob.todecimal(random.normal(10, 1))
                    for _ in range(n_asks)]

        n_bids = random.poisson(lam=100)
        bid_prices = [pylob.todecimal(random.normal(1000, 100))
                      for _ in range(n_bids)]
        bid_qtys = [pylob.todecimal(random.normal(10, 1))
                    for _ in range(n_bids)]

        ask_orders = [pylob.OrderParams(
            pylob.OrderSide.ASK, p, q) for p, q in zip(ask_prices, ask_qtys)]
        bid_orders = [pylob.OrderParams(
            pylob.OrderSide.BID, p, q) for p, q in zip(bid_prices, bid_qtys)]
        orders = (ask_orders + bid_orders)

        random.shuffle(orders)
        ob.process_many(orders)

        print(ob)
        time.sleep(0.1)

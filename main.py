import time
import cProfile
from scipy.stats import genpareto, norm, poisson
from random import shuffle

import pylob as lob
from pylob import OrderParams, OrderSide

def genorders(n):
    Orders = []

    for t in range(n):
        start = time.perf_counter()

        # LIMIT ORDERS
        n_asks = poisson.rvs(100)
        n_bids = poisson.rvs(100)

        loc = 1000

        ask_prices = genpareto.rvs(-0.1, loc=loc, scale=10, size=n_asks)
        bid_prices = -genpareto.rvs(-0.1, loc=loc, scale=10, size=n_bids) + 2*loc

        ask_quantities = norm.rvs(loc=100, scale=10, size=n_asks)
        bid_quantities = norm.rvs(loc=100, scale=10, size=n_bids)

        asks = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_prices, ask_quantities)]
        bids = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_prices, bid_quantities)]

        limits = asks.copy() + bids.copy()

        # MARKET ORDERS
        n_asks = poisson.rvs(10)
        n_bids = poisson.rvs(10)

        ask_prices = norm.rvs(loc=1000, scale=10, size=n_asks)
        bid_prices = norm.rvs(loc=1000, scale=10, size=n_bids)

        ask_quantities = norm.rvs(loc=100, scale=10, size=n_asks)
        bid_quantities = norm.rvs(loc=100, scale=10, size=n_bids)

        asks = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_prices, ask_quantities)]
        bids = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_prices, bid_quantities)]

        markets = asks + bids

        orders = limits + markets
        shuffle(orders)

        Orders.append(orders)

    return Orders

def simulate(orders, display=True):
    orderbook = lob.OrderBook('Simulation')
    query = Query(orderbook)
    query.start()

    for o in orders:
        results = orderbook.process_many(o)
        time.sleep(1.5)

    query.stop()

from threading import Thread

class Query(Thread):
    def __init__(self, ob):
        super().__init__()
        self.ob = ob
        self.s = False

    def stop(self): self.s = True

    def run(self):
        while not self.s:
            print(self.ob, flush=True)
            time.sleep(1)

if __name__ == "__main__":
    n = 10
    orders = genorders(n)
    #cProfile.run('simulate(n, orders, display=False)', sort='time')
    simulate(orders)

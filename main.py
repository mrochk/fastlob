import time
import cProfile
from scipy.stats import genpareto, norm, poisson
from random import shuffle

import pylob
from pylob import OrderBook, OrderParams, OrderSide

def simulation(n):
    orderbook = OrderBook('Simulation')

    for t in range(n):
        start = time.perf_counter()

        # LIMIT ORDERS
        n_asks = poisson.rvs(100)
        n_bids = poisson.rvs(100)

        ask_prices = genpareto.rvs(-0.1, loc=1000, scale=10, size=n_asks)
        bid_prices = -genpareto.rvs(-0.1, loc=1000, scale=10, size=n_bids) + 2000

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

        #ask_quantities = [100] * n_asks
        #bid_quantities = [100] * n_bids

        asks = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_prices, ask_quantities)]
        bids = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_prices, bid_quantities)]

        markets = asks + bids

        orders = limits + markets
        shuffle(orders)

        r = orderbook.process_many(orders)

        end = time.perf_counter()
        duration = end - start

        print(orderbook, flush=True)
        print(f'    t = {round(orderbook.clock(), 1)}s')
        print()

        time.sleep(0.5 - duration)

if __name__ == "__main__":
    #cProfile.run('simulation(1000)', sort='time')
    simulation(100)

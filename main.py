import time
import matplotlib.pyplot as plt
from scipy.stats import genpareto, norm, poisson
from random import shuffle
import cProfile

import pylob
from pylob import OrderBook, OrderParams, OrderSide

def simulation(n):
    orderbook = OrderBook()

    for t in range(n):

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

        asks = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_prices, ask_quantities)]
        bids = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_prices, bid_quantities)]

        markets = asks + bids

        orders = limits + markets
        shuffle(orders)

        orderbook.process_many(orders)

        print(orderbook)
        time.sleep(1)


if __name__ == "__main__":
    # cProfile.run('simulation(10)', sort='time')
    simulation(100)

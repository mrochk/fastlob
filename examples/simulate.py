import random, time, os
from scipy import stats

from fastlob import Orderbook, OrderParams, OrderSide

def generate_orders(T: int, midprice: float):
    result = list()
    
    for _ in range(T):
    
        n_ask_limits = stats.poisson.rvs(500)
        n_bid_limits = stats.poisson.rvs(500)
    
        ask_limits_price = stats.expon.rvs(loc=midprice, scale=1, size=n_ask_limits)
        bid_limits_price = -stats.expon.rvs(loc=midprice, scale=1, size=n_bid_limits) + 2*midprice
    
        ask_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_ask_limits)
        bid_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_bid_limits)
    
        ask_limits_params = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_limits_price, ask_limits_quantities)]
        bid_limits_params = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_limits_price, bid_limits_quantities)]
    
        n_markets = stats.poisson.rvs(100)
    
        markets_price = stats.norm.rvs(loc=midprice, scale=2, size=n_markets)
        markets_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_markets)
        markets_bid_or_ask = [random.choice((OrderSide.BID, OrderSide.ASK)) for _ in range(n_markets)]
    
        markets_params = [OrderParams(s, p, q) for (s, p, q) in zip(markets_bid_or_ask, markets_price, markets_quantities)]
    
        orders = ask_limits_params + bid_limits_params + markets_params
        random.shuffle(orders)
        
        result.append(orders)
        
    return result

def simulate(orders: list, speed: float):
    ob = Orderbook('Simulation')
    ob.start()

    for o in orders:
        ob.process_many(o)
        print()
        ob.render()
        time.sleep(speed)
        os.system('clear')
        
    ob.stop()

if __name__ == '__main__':
    orders = generate_orders(10, 100)
    simulate(orders, 0.5)
import time
import random

import pylob

if __name__ == '__main__':
    ob = pylob.OrderBook()

    for t in range(1000):
        asks = random.randint(0, 50)
        ask_prices = [pylob.todecimal(random.normalvariate(1000, 100)) for _ in range(asks)]
        ask_qtys = [pylob.todecimal(random.normalvariate(100, 10)) for _ in range(asks)]

        bids = random.randint(0, 50)
        bid_prices = [pylob.todecimal(random.normalvariate(1000, 100)) for _ in range(bids)]
        bid_qtys = [pylob.todecimal(random.normalvariate(100, 10)) for _ in range(bids)]

        ask_orders = [pylob.OrderParams(pylob.OrderSide.ASK, p, q) for p, q in zip(ask_prices, ask_qtys)]
        bid_orders = [pylob.OrderParams(pylob.OrderSide.BID, p, q) for p, q in zip(bid_prices, bid_qtys)]
        orders = (ask_orders + bid_orders)

        random.shuffle(orders)

        ob.process_many(orders)
        
        #print(f't={t}')
        print(ob)
        time.sleep(0.1)
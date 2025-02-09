from time import perf_counter
from functools import wraps

from pylob import (
    OrderBook,
    OrderParams,
    OrderSide,
)

 
def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        time_start = perf_counter()
        result = func(*args, **kwargs)
        time_end = perf_counter()
        time_duration = time_end - time_start
        name = func.__name__
        print(f'{name} took {time_duration:.3f} seconds to complete')
        return result
    return wrapper


def benchmark1():
    '''Place 100_000 orders at the same limit, on both sides.
    '''
    PRICE_BID = 1000
    PRICE_ASK = 2000
    QTY = 1000

    ob = OrderBook()
    bids = [OrderParams(OrderSide.BID, PRICE_BID, QTY) for _ in range(100_000)]
    asks = [OrderParams(OrderSide.ASK, PRICE_ASK, QTY) for _ in range(100_000)]

    @benchmark
    def Benchmark1(): ob.process_many(asks + bids)
    Benchmark1()


def benchmark2():
    '''Place 100_000 orders at different limits, on both sides.
    '''
    PRICE_BID = 200_000
    PRICE_ASK = 300_000
    QTY = 1000

    ob = OrderBook()
    bids = [OrderParams(OrderSide.BID, PRICE_BID - i, QTY) for i in range(100_000)]
    asks = [OrderParams(OrderSide.ASK, PRICE_ASK + i, QTY) for i in range(100_000)]

    @benchmark
    def Benchmark2(): ob.process_many(asks + bids)
    Benchmark2()

benchmarks = [
    benchmark1,
    benchmark2,
]

if __name__ == '__main__':
    for b in benchmarks: b()

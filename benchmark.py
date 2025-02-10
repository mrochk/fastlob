from time import perf_counter
from functools import wraps
import random
import cProfile

from pylob import OrderBook, OrderParams, OrderSide


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

if __name__ == '__main__': raise NotImplemented
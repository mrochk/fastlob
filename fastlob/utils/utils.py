import time
from decimal import Decimal
from numbers import Number

from fastlob.consts import DECIMAL_PRECISION

def todecimal(n: Number | str) -> Decimal:
    '''Wrapper around the Decimal constructor to properly round numbers to user defined precision.'''
    if not isinstance(n, Number | str): raise TypeError("invalid type to be converted to decimal")

    dec = Decimal.from_float(n) if isinstance(n, float) else Decimal(n)
    exp = Decimal(f'0.{"0"*DECIMAL_PRECISION}')

    return dec.quantize(exp)

def zero(): return Decimal('0')

def time_asint() -> int: return int(time.time())

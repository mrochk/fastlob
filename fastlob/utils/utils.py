'''Global utility functions.'''

import time
from decimal import Decimal
from numbers import Number

from fastlob.consts import DECIMAL_PRECISION_PRICE, DECIMAL_PRECISION_QTY

def todecimal_price(price: Number | str) -> Decimal:
    '''Wrapper around the Decimal constructor to properly round numbers to user defined precision.'''

    return _todecimal(price, DECIMAL_PRECISION_PRICE)

def todecimal_quantity(price: Number | str) -> Decimal:
    '''Wrapper around the Decimal constructor to properly round numbers to user defined precision.'''

    return _todecimal(price, DECIMAL_PRECISION_QTY)

def _todecimal(price: Number | str, precision: int) -> Decimal:
    '''Wrapper around the Decimal constructor to properly round numbers to user defined precision.'''

    if not isinstance(price, Number | str): raise TypeError("invalid type to be converted to decimal")

    dec = Decimal.from_float(price) if isinstance(price, float) else Decimal(price)
    exp = Decimal(f'0.{"0"*precision}')

    return dec.quantize(exp)

def zero():
    '''Decimal('0')'''

    return Decimal('0')

def time_asint() -> int:
    '''int(time.time())'''

    return int(time.time())

from decimal import Decimal
from numbers import Number
from typing import Union

DEFAULT_DECIMAL_PRECISION: int = 2

MIN_VALUE = UNIT = Decimal('0.01')

MAX_VALUE = Decimal(10e10)

num = Union[Number | Decimal]  # helper typing constant

def zero(): return Decimal('0')

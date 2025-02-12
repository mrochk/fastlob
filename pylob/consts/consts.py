from decimal import Decimal
from numbers import Number
from typing import Union

num = Union[Number | Decimal]  # helper typing constant

DEFAULT_DECIMAL_PRECISION: int = 2

MIN_VALUE = UNIT = Decimal('0.01')

MAX_VALUE = Decimal(10e10)

def zero(): return Decimal('0')
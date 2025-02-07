from decimal import Decimal
from numbers import Number
from typing import Union

num = Union[Number | Decimal]  # helper typing constant

ZERO: Decimal = Decimal('0')

DEFAULT_DECIMAL_PRECISION: int = 2

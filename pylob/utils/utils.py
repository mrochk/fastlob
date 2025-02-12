from typing import Iterable
from decimal import Decimal
from numbers import Number

from pylob.consts import DEFAULT_DECIMAL_PRECISION


def todecimal(n: Number | str | Iterable[Number | str]) -> Decimal:
    '''Wrapper around the Decimal constructor.

    Args:
        f (num): The numerical value to convert to Decimal object.

    Returns:
        Decimal: The converted Decimal
    '''
    if not isinstance(n, Number | str | Iterable):
        raise TypeError()

    if isinstance(n, Iterable):
        return [todecimal(x) for x in n]

    dec = Decimal.from_float(n) if isinstance(n, float) else Decimal(n)
    exp = Decimal(f'0.{"0"*DEFAULT_DECIMAL_PRECISION}')

    return dec.quantize(exp)

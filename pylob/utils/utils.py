from typing import Iterable
from decimal import Decimal

from pylob.consts import num, DEFAULT_DECIMAL_PRECISION


def todecimal(f: num | str | Iterable) -> Decimal:
    '''Wrapper around the Decimal constructor.

    Args:
        f (num): The numerical value to convert to Decimal object.

    Returns:
        Decimal: The converted Decimal
    '''
    if not isinstance(f, num | str | Iterable): raise TypeError()
    if isinstance(f, Iterable):
        return [todecimal(x) for x in f]

    dec = Decimal.from_float(f) if isinstance(f, float) else Decimal(f)
    exp = Decimal(f'0.{"0"*DEFAULT_DECIMAL_PRECISION}')

    return dec.quantize(exp)

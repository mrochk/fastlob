from decimal import Decimal

from pylob.consts import num, DEFAULT_DECIMAL_PRECISION


def todecimal(f: num | str) -> Decimal:
    '''Wrapper around the Decimal constructor.

    Args:
        f (num): The numerical value to convert to Decimal object.

    Returns:
        Decimal: The converted Decimal
    '''
    dec = Decimal.from_float(f) if isinstance(f, float) else Decimal(f)
    exp = Decimal(f'0.{"0"*DEFAULT_DECIMAL_PRECISION}')
    return dec.quantize(exp)

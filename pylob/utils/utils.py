from decimal import Decimal

from pylob.consts import DEFAULT_DECIMAL_PRECISION, num

def todecimal(f : num) -> Decimal:
    dec = Decimal.from_float(f) if isinstance(f, float) else Decimal(f)
    exp = Decimal(f'0.{"0"*DEFAULT_DECIMAL_PRECISION}')
    return dec.quantize(exp) 
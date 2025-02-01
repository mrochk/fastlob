from decimal import Decimal
import uuid

from pylob.consts import DECIMAL_PRECISION, num

def todecimal(f : num) -> Decimal:
    dec = Decimal.from_float(f) if isinstance(f, float) else Decimal(f)
    exp = Decimal(f'0.{"0"*DECIMAL_PRECISION}')
    return dec.quantize(exp) 
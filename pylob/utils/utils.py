from decimal import Decimal
import uuid

from ..consts import DECIMAL_PRECISION

def todecimal(f : (float | int | Decimal)) -> Decimal:
    dec = Decimal.from_float(f) if isinstance(f, float) else Decimal(f)
    exp = Decimal(f'0.{"0"*DECIMAL_PRECISION}')
    return dec.quantize(exp) 

def gen_uuid():
    return uuid.uuid4()
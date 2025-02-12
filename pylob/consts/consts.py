from decimal import Decimal

DEFAULT_DECIMAL_PRECISION: int = 2

MIN_VALUE = UNIT = Decimal('0.' + ('0' * (DEFAULT_DECIMAL_PRECISION-1)) + '1')

MAX_VALUE = Decimal(10e10)

ORDERS_ID_SIZE = 8

def zero(): return Decimal('0')

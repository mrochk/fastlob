'''Various constants and parameters used in the project.'''

import os
from decimal import Decimal

ENV_DECIMAL_PRECISION_PRICE: str = 'FASTLOB_DECIMAL_PRECISION_PRICE'

ENV_DECIMAL_PRECISION_QTY: str = 'FASTLOB_DECIMAL_PRECISION_QTY'

DECIMAL_PRECISION_DEFAULT: int = 2

def _get_precision(env_varname: str) -> int:
    precision = os.environ.get(env_varname)
    return int(precision) if precision else DECIMAL_PRECISION_DEFAULT

DECIMAL_PRECISION_PRICE: int = _get_precision(ENV_DECIMAL_PRECISION_PRICE)

DECIMAL_PRECISION_QTY: int = _get_precision(ENV_DECIMAL_PRECISION_QTY)

TICK_SIZE_PRICE = Decimal('0.' + ('0' * (DECIMAL_PRECISION_PRICE - 1)) + '1')

TICK_SIZE_QTY = Decimal('0.' + ('0' * (DECIMAL_PRECISION_QTY - 1)) + '1')

MAX_VALUE = Decimal(int(10e10))

ORDERS_ID_SIZE = 8

DEFAULT_LIMITS_VIEW = 10

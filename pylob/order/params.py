from decimal import Decimal
from dataclasses import dataclass
from typing import Optional

from pylob.enums import OrderSide, OrderType
from pylob.utils import num, todecimal

@dataclass(repr=True)
class OrderParams:
    side     : OrderSide
    price    : Decimal
    quantity : Decimal
    type     : OrderType = OrderType.GTC
    expiry   : Optional[float] = None

    def __init__(self, side : OrderSide, price : num, quantity : num,
                 type : OrderType = OrderType.GTC, 
                 expiry : Optional[float] = None):

        OrderParams.check_args(side, price, quantity, type, expiry)

        self.side     = side
        self.price    = todecimal(price)
        self.quantity = todecimal(quantity)
        self.type     = type
        self.expiry   = expiry

    @staticmethod
    def check_args(side : OrderSide, price : num, quantity : num, 
                   type : OrderType, expiry : Optional[float]):
        if not isinstance(side, OrderSide): raise TypeError()
        if not isinstance(price,      num): raise TypeError()
        if not isinstance(quantity,   num): raise TypeError()
        if not isinstance(type, OrderType): raise TypeError()
        if not isinstance(expiry,   Optional[float]): raise TypeError()

        if price <= 0: 
            raise ValueError(f'price ({price}) must be strictly positive')

        if quantity <= 0: 
            raise ValueError(f'quantity ({quantity}) must be strictly positive')

    def unwrap(self) -> tuple[Decimal, Decimal, OrderType, float]:
        return (self.price, self.quantity, self.type, self.expiry)
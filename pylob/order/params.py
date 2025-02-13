from numbers import Number
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional

from pylob.enums import OrderSide, OrderType
from pylob.utils import todecimal
from pylob.consts import MIN_VALUE, MAX_VALUE

@dataclass(repr=True)
class OrderParams:
    '''This class is used for instantiating orders, it is necessary because we do not want to have the system 
    performing any safety checks, or at least it should have to do as few as possible. Therefore this class is used to 
    enforce the user to provide valid order parameters.'''

    side: OrderSide
    price: Decimal
    quantity: Decimal
    type: OrderType = OrderType.GTC
    expiry: Optional[float] = None

    def __init__(self, side: OrderSide, price: Number, quantity: Number, type: OrderType = OrderType.GTC,
                 expiry: Optional[float] = None):

        OrderParams.check_args(side, price, quantity, type, expiry)

        self.side = side
        self.price = todecimal(price)
        self.quantity = todecimal(quantity)
        self.type = type
        self.expiry = expiry

    @staticmethod
    def check_args(side: OrderSide, price: Number, quantity: Number, type: OrderType, expiry: Optional[float]):
        '''Check for args correctness. This method is very important, since we do not check for this after the 
        OrderParams object is created.'''
        if not isinstance(side, OrderSide): raise TypeError()
        if not isinstance(price, Number): raise TypeError()
        if not isinstance(quantity, Number): raise TypeError()
        if not isinstance(type, OrderType): raise TypeError()
        if expiry and not isinstance(expiry, float): raise TypeError()

        if price < MIN_VALUE: raise ValueError(f"price ({price}) must be greater than 0.01")

        if quantity < MIN_VALUE: raise ValueError(f"quantity ({quantity}) must be greater than 0.01")

        if price > MAX_VALUE: raise ValueError(f"price ({price}) is too large")

        if quantity > MAX_VALUE: raise ValueError(f"quantity ({quantity}) is too large")

    def unwrap(self) -> tuple[Decimal, Decimal, OrderType, Optional[float]]:
        return self.price, self.quantity, self.type, self.expiry

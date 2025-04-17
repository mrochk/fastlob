'''Utility functions for side.'''

from numbers import Number
from decimal import Decimal

from fastlob.utils import zero, todecimal_price, todecimal_quantity

def todecimal_pair(pair: tuple[Number, Number]) -> tuple[Decimal, Decimal]:
    price, volume = pair
    return todecimal_price(price), todecimal_quantity(volume)

def check_update_pair(pair) -> None:
    '''Raise an exception if the pair provided can not be processed as update.'''

    if not isinstance(pair, tuple) or len(pair) != 2:
        raise ValueError('must be pairs of (price, volume)')

    price, volume = pair

    if not isinstance(price, Number) or not isinstance(volume, Number):
        raise ValueError('(price, volume) must be both instances of Number')

    if todecimal_price(price) <= zero(): raise ValueError(f'price must be strictly positive but is {price}')

def check_snapshot_pair(pair):
    '''Raise an exception if the pair provided can not be processed as snapshot.'''

    check_update_pair(pair)

    _, volume = pair
    if volume <= 0: raise ValueError(f'volume must be strictly positive but is {volume}')

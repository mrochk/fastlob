from numbers import Number

def check_update_pair(pair):
    if not isinstance(pair, tuple) or len(pair) != 2:
        raise ValueError('must be pairs of (price, volume)')

    price, volume = pair

    if not isinstance(price, Number) or not isinstance(volume, Number):
        raise ValueError('(price, volume) must be both instances of Number')

    if price <= 0: raise ValueError(f'price must be strictly positive but is {price}')

def check_snapshot_pair(pair):
    check_update_pair(pair)

    _, volume = pair
    if volume <= 0: raise ValueError(f'volume must be strictly positive but is {volume}')
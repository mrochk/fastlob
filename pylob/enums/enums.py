from enum import Enum


class OrderSide(Enum):
    '''The side of an order/limit, can be BID or ASK.'''
    BID = False
    ASK = True


class OrderType(Enum):
    '''The type of the order, can be FOK, GTC or GTD.'''
    FOK = 1,
    '''A fill or kill (FOK) order is a conditional order requiring the 
    transaction to be executed immediately and to its full amount at a stated 
    price. If any of the conditions are broken, then the order must be 
    automatically canceled (kill) right away.'''
    GTC = 2,
    '''A Good-Til-Cancelled (GTC) order is an order to buy or sell a stock that 
    lasts until the order is completed or canceled.
    '''
    GTD = 3,
    '''A 'Good-Til-Day' order is a type of order that is active until its 
    specified date (UTC seconds timestamp), unless it has already been 
    fulfilled or cancelled. There is a security threshold of one minute: 
    If the order needs to expire in 30 seconds the correct expiration value is: 
    now + 1 minute + 30 seconds
    '''


class OrderStatus(Enum):
    '''The status of an order.'''
    CREATED = 1
    IN_LINE = 2
    FILLED = 3
    CANCELED = 4
    PARTIAL = 5

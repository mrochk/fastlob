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
    now + 1 minute + 30 seconds.
    '''


class OrderStatus(Enum):
    '''The status of an order.'''
    CREATED = 1, 
    '''Order created but not in a limit queue yet, or executed.'''
    PENDING = 2,
    '''Order in line to be filled but not modified in any ways yet.'''
    PARTIAL = 3,
    '''Order partially filled.'''
    FILLED = 4,
    '''Order entirely filled, removed from the limit.'''
    CANCELED = 5,
    '''Order canceled, can not be fully or partially fileld anymore.'''

    @staticmethod
    def valid_states() -> set:
        return {OrderStatus.CREATED, OrderStatus.PENDING, OrderStatus.PARTIAL}

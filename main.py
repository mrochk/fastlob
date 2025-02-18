import time
import cProfile
import threading

import pylob as lob
from pylob import OrderType

if __name__ == "__main__": 
    FOK = OrderType.FOK
    GTD = OrderType.GTD
    GTC = OrderType.GTC

    ob = lob.OrderBook('Test')
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 125, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 125, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 125, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 125, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 125, 100))

    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 110, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 110, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 110, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 110, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 110, 100))

    print('BEFORE:')
    print(ob.view())

    print('VALID BUY 425 @ 125:')
    valid_fok_order = lob.OrderParams(lob.OrderSide.BID, 125, 425, otype=FOK)
    result_valid = ob.process_one(valid_fok_order)
    print(ob.view())
    print(result_valid)

    print('INVALID BUY 1 @ 120:')
    invalid_fok_order_price = lob.OrderParams(lob.OrderSide.BID, 120, 1, otype=FOK)
    result_price = ob.process_one(invalid_fok_order_price)
    print(ob.view())
    print(result_price)

    print('INVALID BUY 525 @ 125:')
    invalid_fok_order_qty = lob.OrderParams(lob.OrderSide.BID, 125, 525, otype=FOK)
    result_qty = ob.process_one(invalid_fok_order_qty)
    print(ob.view())
    print(result_qty)


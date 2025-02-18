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

    valid_fok_order = lob.OrderParams(lob.OrderSide.BID, 125, 425, otype=FOK)


    

    print(ob.view())
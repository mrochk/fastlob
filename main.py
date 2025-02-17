import time
import cProfile
import threading

import pylob as lob

if __name__ == "__main__": 
    ob = lob.OrderBook('Test')
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 100, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 100, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 100, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 100, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.ASK, 100, 100))

    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 90, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 90, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 90, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 90, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 90, 100))

    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 81, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 82, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 83, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 84, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 85, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 87, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 89, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 80, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 79, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 78, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 77, 100))
    ob.process_one(lob.OrderParams(lob.OrderSide.BID, 76, 100))
    print(ob)
    exit(0)

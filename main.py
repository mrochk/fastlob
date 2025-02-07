import pylob

if __name__ == '__main__': 
    ob = pylob.OrderBook()

    for i in range(20):
        ob.process_one(pylob.OrderParams(pylob.OrderSide.ASK, 1100+i + (i/10) + (i/100), 100))
        ob.process_one(pylob.OrderParams(pylob.OrderSide.BID, 999 - i, 100))

    print(ob)
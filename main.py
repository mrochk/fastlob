import pylob

if __name__ == '__main__': 

    ob = pylob.OrderBook()

    ob.process_many([
        pylob.OrderParams(500, 30, pylob.OrderSide.BID, pylob.OrderType.GTC),
        pylob.OrderParams(499, 30, pylob.OrderSide.BID, pylob.OrderType.GTC),
        pylob.OrderParams(498, 30, pylob.OrderSide.BID, pylob.OrderType.GTC),

        pylob.OrderParams(510, 30, pylob.OrderSide.ASK, pylob.OrderType.GTC),
        pylob.OrderParams(511, 30, pylob.OrderSide.ASK, pylob.OrderType.GTC),
        pylob.OrderParams(512, 30, pylob.OrderSide.ASK, pylob.OrderType.GTC),
    ])

    print(ob)

    result = ob.process_one(
        pylob.OrderParams(510, 25, pylob.OrderSide.BID)
    )

    print(result)

    result = ob.process_one(
        pylob.OrderParams(510, 30, pylob.OrderSide.BID)
    )

    print(result)

    result = ob.process_one(
        pylob.OrderParams(511, 40, pylob.OrderSide.BID)
    )

    print(result)

    print(ob)
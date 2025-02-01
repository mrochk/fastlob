import pylob

if __name__ == '__main__':
    ob = pylob.OrderBook()

    for _ in range(10):
        for i in range(10):
            ob.place_order(
                price=10-i, 
                quantity=10, 
                type=pylob.OrderType.FOK,
                side=pylob.OrderSide.BID
            )
            ob.place_order(
                price=12+i, 
                quantity=10, 
                type=pylob.OrderType.FOK,
                side=pylob.OrderSide.ASK
            )

    ob.display()

    print(ob.midprice())

    print(ob.spread())
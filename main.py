import pylob

if __name__ == '__main__':
    ob = pylob.OrderBook('BTC/USDT')

    for _ in range(10):
        for i in range(10):

            ob.process(
                price=10-i, 
                quantity=10, 
                type=pylob.OrderType.GTC,
                side=pylob.OrderSide.BID
            )

            ob.process(
                price=12+i, 
                quantity=10, 
                type=pylob.OrderType.GTC,
                side=pylob.OrderSide.ASK
            )

    marketorder = pylob.AskOrder(
        price=10,
        quantity=100,
        type=pylob.OrderType.FOK
    )

    ob.process_order(marketorder)

    print(ob)
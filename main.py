import pylob as lob
from pylob import OrderSide, OrderType

if __name__ == '__main__':
    # initializing an order-book
    ob = lob.OrderBook('EUR/GBP')

    orders = [
        lob.OrderParams(110, 100, lob.OrderSide.ASK),
        lob.OrderParams(110.5, 100, lob.OrderSide.ASK),
        lob.OrderParams(111, 100, lob.OrderSide.ASK),
        lob.OrderParams(111.5, 100, lob.OrderSide.ASK),
        lob.OrderParams(112, 100, lob.OrderSide.ASK),

        lob.OrderParams(100,   100,   lob.OrderSide.BID),
        lob.OrderParams(100.5, 100, lob.OrderSide.BID),
        lob.OrderParams(101,   100,   lob.OrderSide.BID),
        lob.OrderParams(101.5, 100, lob.OrderSide.BID),
        lob.OrderParams(102,   100,   lob.OrderSide.BID),
    ]

    for _ in range(2): ob.process_many(orders)

    print(ob); print()

    marketo = lob.OrderParams(
        110, 110, OrderSide.BID
    )

    ob.process_one(marketo)

    print(ob)
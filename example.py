import time, logging

from fastlob import Orderbook, OrderParams, OrderSide, OrderType

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    lob = Orderbook(name='ABCD'); lob.start()

    params = OrderParams(
        side=OrderSide.BID,
        price=123.32, 
        quantity=3.4,
        otype=OrderType.GTD, 
        expiry=time.time() + 120 
    )

    result = lob(params); assert result.success()

    status, qty_left = lob.get_status(result.orderid())
    print(f'Current order status: {status.name}, quantity left: {qty_left}.\n')

    lob.render()

    lob.stop() 

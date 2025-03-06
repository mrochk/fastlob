import time, logging

from fastlob import Orderbook, OrderParams, OrderSide, OrderType

if __name__ == '__main__':
    lob = Orderbook(name='ABCD', log_level=logging.INFO)

    lob.start()

    params = OrderParams(
        side=OrderSide.BID,
        price=123.32, 
        quantity=3.4,
        otype=OrderType.GTD, 
        expiry=time.time() + 120 
    )

    result = lob(params)
    assert result.success()

    status, quantity_left = lob.get_status(result.orderid())
    print(f'Current order status: {status.name}, quantity left: {quantity_left}.\n')

    lob.render()

    lob.stop() 

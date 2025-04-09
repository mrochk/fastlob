import time, logging

from fastlob import Orderbook, OrderParams, OrderSide, OrderType

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # set maximum logging level 

    lob = Orderbook(name='ABCD', start=True) # create a lob an start it

    # create an order
    params = OrderParams(
        side=OrderSide.BID,
        price=123.32,
        quantity=3.4,
        otype=OrderType.GTD, 
        expiry=time.time() + 120 # order will expire in two minutes
    )

    result = lob(params); assert result.success() # place order

    status, qty_left = lob.get_status(result.orderid()) # query status of order
    print(f'Current order status: {status.name}, quantity left: {qty_left}.\n')

    lob.render() # pretty-print the lob 

    lob.stop() # stop background processes

import time
import logging

import fastlob as lob

if __name__ == '__main__':

    book = lob.Orderbook(
        name='My Order-Book',
        log_level=logging.WARNING # default logging level, change to INFO or WARNING to increase or reduce
    )

    book.start()

    # every order must be created this way 
    order_params = lob.OrderParams(
        side=lob.OrderSide.BID,
        price=123.32, # by default runs at 2 digits decimal precision
        quantity=3.4,
        otype=lob.OrderType.GTD, # good-till-date order
        expiry=time.time() + 120 # expires in two minutes
    )

    # -> at this point an exception will be raised if invalid attributes are provided

    result = book(order_params) # let the book process the order

    assert result.success() # result object can be used to see various infos about the order execution

    order_id = result.orderid() # unique id is used to query our order after it's been placed
    status, quantity_left = book.get_order_status(order_id)
    print(f'Current status of the order: {status.name}, quantity left: {quantity_left}.\n')

    book.render() # pretty-print the book

    book.stop()
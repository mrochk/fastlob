import time
from fastlob import OrderBook, OrderParams, OrderSide, OrderType

if __name__ == '__main__':

    book = OrderBook('My Order-Book')
    book.start()

    order_params = OrderParams(
        side = OrderSide.BID,
        price = 123.32,
        quantity = 3.4,
        otype = OrderType.GTD, # good-till-date order
        expiry = time.time() + 120 # order expires in two minutes
    )

    # -> at this point an exception will be raised if invalid attributes are provided

    result = book(order_params) # let the book process the order

    assert result.success() # result object can be used to see various infos about the order execution

    order_id = result.order_id()
    status, quantity_left = book.get_order_status(order_id)

    print(f'Current status of the order: {status}, quantity left: {quantity_left}.')

    print(book.view()) # pretty-print the book
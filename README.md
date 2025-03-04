# fastlob | Fast Python Limit-Order-Book
**Fast &amp; minimalist fixed decimal precision limit-order-book (LOB) implementation in pure Python with almost no dependencies.**

<br>

<img src="https://github.com/mrochk/pylob/raw/main/logo.png" width=700>

*Package currently in development, bugs are expected.*

The goal is to build an efficient easy to use package with a clean and comprehensible API. 

We aim to keep it minimalist and simple, while keeping reasonable performances (for a pure Python implementation). We intend the final project to contain no more than ~1000 lines of code.

<!-- <br> -->

<!-- <img src="https://github.com/mrochk/pylob/raw/main/ss.png" width=450> -->

We implement three types of orders: *FOK*, *GTC* and *GTD*. Every order is defined as a limit order, but will be executed as a market order if its price matches the best (bid or ask) limit price in the book.

*In the case of GTD orders, the book only supports whole seconds for the order expiry (order can not be set to expire in 3.8 seconds, it will be rounded to 4).*

# Usage

This book runs at a fixed decimal precision through the Python `decimal` package. The precision can be set via the `PYLOB_DECIMAL_PRECISION` environment variable, the default value is 2.

To be able to use this project, clone the repository and install the requirements: 
```bash
git clone git@github.com:mrochk/pylob.git
cd pylob
pip install -r requirements.txt
```

To run tests, use `make test` or `python3 -m unittest discover test`.

***Placing an order***
```python
# example.py
import time
import fastlob as lob

book = lob.OrderBook(
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

order_id = result.order_id() # unique id is used to query our order after it's been placed
status, quantity_left = book.get_order_status(order_id)
print(f'Current status of the order: {status.name}, quantity left: {quantity_left}.\n')

print(book.view()) # pretty-print the book

book.stop()
```

***

*Lines count:*
```
   94 fastlob/engine/engine.py
    1 fastlob/engine/__init__.py
   18 fastlob/utils/utils.py
    1 fastlob/utils/__init__.py
   65 fastlob/order/params.py
    1 fastlob/order/__init__.py
  161 fastlob/order/order.py
   52 fastlob/enums/enums.py
    1 fastlob/enums/__init__.py
   64 fastlob/orderbook/result.py
  484 fastlob/orderbook/orderbook.py
    0 fastlob/orderbook/__init__.py
   19 fastlob/consts/consts.py
    1 fastlob/consts/__init__.py
  140 fastlob/limit/limit.py
    1 fastlob/limit/__init__.py
  162 fastlob/side/side.py
    1 fastlob/side/__init__.py
    4 fastlob/__init__.py
 1270 total
```

***

# TODOs:

As mentioned earlier, this package is still in early development, and contributions are more than welcome.

The main tasks that have to be done are:
- **More and better testing for edge cases. In fact, some tests have to be rewritten too.**
- **Benchmarking / profiling to have an idea of the performance, and see where it's slow.**
- **Some parts probably need to be rewritten in a cleaner way.**
- **Publish the package on pypi.**

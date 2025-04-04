# fastlob | Fast Limit-Order-Book in Python
**Fast &amp; minimalist fixed decimal precision limit-order-book (LOB) implementation in pure Python with almost no dependencies.**

<br>

<img src="https://github.com/mrochk/pylob/raw/main/logo.png" width=800>

*Package currently in development, bugs are expected.*

*The main branch does not implement multi-threaded order processing because it is still being developed on the `multithreading` branch, check out this branch, or the corresponding issue for more infos.*

The goal is to build an efficient easy to use package with a clean and comprehensible API. 

We aim to keep it minimalist and simple, while keeping reasonable performances (for a pure Python implementation). We intend the final project to contain no more than ~1000 lines of code.

We implement three types of orders: *FOK*, *GTC* and *GTD*. Every order is defined as a limit order, but will be executed as a market order if its price matches the best (bid or ask) limit price in the book.

*In the case of GTD orders, the book only supports whole seconds for the order expiry (order can not be set to expire in 3.8 seconds, it will be rounded to 4).*

## Installation

The package is now available on [PyPI](https://pypi.org/project/fastlob/), you can simply install it using
```
pip install fastlob
```

Otherwise, one can install it from source
```bash
git clone git@github.com:mrochk/fastlob.git
cd fastlob
pip install -r requirements.txt
pip install .
```

## Testing

To run the tests and check that everything is okay, run `make test` or `python3 -m unittest discover test`.

## Usage

This book runs at a fixed decimal precision through the Python `decimal` package. The precision (also called *Tick Size*) can be set via the `PYLOB_DECIMAL_PRECISION` environment variable, the default value is 2.

```python
# examples/basics.py

import time, logging

from fastlob import Orderbook, OrderParams, OrderSide, OrderType

logging.basicConfig(level=logging.INFO) # maximum logging

lob = Orderbook(name='ABCD') # init lob

lob.start() # start background processes

# every order must be created this way 
params = OrderParams(
    side=OrderSide.BID, # is it a buy or sell order
    price=123.32, quantity=3.42, # by default runs at 2 digits decimal precision
    otype=OrderType.GTD, # good-till-date order
    expiry=time.time() + 120 # order will expire in two minutes
    # since order is GTD, expiry must be set to some future timestamp
)

# -> at this point an exception will be raised if invalid attributes are provided

result = lob(params) # let the book process the order
assert result.success() # result object can be used to see various infos about the order execution

# order uuid is used to query our order after it's been placed
status, quantity_left = lob.get_order_status(result.orderid())
print(f'Current order status: {status.name}, quantity left: {quantity_left}.\n')

lob.render() # pretty-print the book

lob.stop() # stop the background processes
```

In the notebook [`simulate.ipynb`](examples/simulate.ipynb) you will find an example of simulating the arrival of many orders using different distributions.

## Contributing

As mentioned earlier, this package is still in early development, and contributions are more than welcome.

Please do not hesitate to contact me, or directly submit a pull request if you'd like to contribute.

## Lines Count
```
  92 fastlob/engine/engine.py
   3 fastlob/engine/__init__.py
  18 fastlob/utils/utils.py
   1 fastlob/utils/__init__.py
  82 fastlob/result/result.py
   1 fastlob/result/__init__.py
  79 fastlob/order/params.py
   1 fastlob/order/__init__.py
  97 fastlob/order/order.py
  56 fastlob/enums/enums.py
   1 fastlob/enums/__init__.py
  20 fastlob/consts/consts.py
   1 fastlob/consts/__init__.py
  99 fastlob/limit/limit.py
   1 fastlob/limit/__init__.py
 140 fastlob/side/side.py
   1 fastlob/side/__init__.py
   5 fastlob/__init__.py
 461 fastlob/lob/orderbook.py
  83 fastlob/lob/utils.py
   1 fastlob/lob/__init__.py
1243 total
```

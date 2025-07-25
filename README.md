# fastlob | Python Limit-Order-Book
<br>

**Fast & minimalist limit-order-book (LOB) implementation in Python, with almost no dependencies.**

<br>

<img src="https://github.com/mrochk/pylob/raw/main/logo.png" width=800>

*Package currently in development, bugs are expected.*

*This is the very first version of the project, the idea was to have a working, correct and clean single-threaded version before making it fast. The next step is to rewrite the core parts in a faster and concurrent fashion.*

*For now, I have decided to keep it written only in Python (no interfacing with C/C++), but that may change in the future.*

***

**Functionalities:**
- Place limit orders.
- Execute market orders.
- Orders can be good-till-cancel (GTC), fill-or-kill (FOK) or good-till-date (GTD).
- Cancel pending or partially filled orders.
- Query order status (pending, filled, partially filled, canceled...).
- Set custom tick size for price and quantities.
- Extract spread, midprice, volume, etc.
- Simulate on historical data.

The goal is to build an efficient and easy to use package, with a clean and comprehensible API. 

We aim to keep it minimalist and simple, while keeping reasonable performances (for a pure Python implementation). We intend the final project to contain no more than ~1000 lines of code.

We implement three types of orders: *FOK*, *GTC* and *GTD*. Every order is initially defined as limit, but will be executed as a market order if its price matches the best (bid or ask) limit price in the book.

*In the case of GTD orders, the book only supports whole seconds for the order expiry (order can not be set to expire in 3.8 seconds, in this case it will be rounded to 4, nearest integer).*

*We do not implement multi-threaded order processing yet, check out the corresponding issue for more infos.*

## Installation

The package is available on [PyPI](https://pypi.org/project/fastlob/), you can simply install it using
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

This book runs at a fixed decimal precision through the Python `decimal` package. The decimal precision (also called *tick size*) can be set via the `FASTLOB_DECIMAL_PRECISION_PRICE` and `FASTLOB_DECIMAL_PRECISION_QTY` environment variables, if not set it defaults to 2.

```python
# examples/basics.py

import time, logging

from fastlob import Orderbook, OrderParams, OrderSide, OrderType

logging.basicConfig(level=logging.INFO) # maximum logging

lob = Orderbook(name='MYLOB', start=True) # init and start lob

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

**For more examples please check out `https://fastlob.com`.**

## Contributing

As mentioned earlier, this package is still in early development, and contributions are more than welcome.

Please do not hesitate to contact me or directly submit a pull request if you'd like to contribute, there are also various issues open on Github.

My e-mail: `mrochkoulets@gmail.com`
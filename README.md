# `pylob` | Python Limit-Order-Book
**Fast &amp; minimalist limit-order-book (LOB) implementation in pure Python.**

*Package currently in development, can not be used yet.*

The goal is to build an efficient, clean and easy to use package for whoever needs to be able to quickly run a limit-order-book in their Python project. 

We aim to keep the API minimalist and simple, while having reasonable performances (for a pure Python implementation). We intend the final project to contain no more than ~1000 lines of code.

<img src="ss.png" width=400>

We implement three types of orders: *FOK*, *GTC* and *GTD*. Every order is defined as a limit order, but will be executed as a market order if its price matches the best (bid or ask) limit price in the book.

<a href="TODO.md">TODO</a>

# Usage

This book runs at a fixed decimal precision through the Python `decimal` package. The precision can be set via the `PYLOB_DECIMAL_PRECISION` environment variable, it's default value being 2.

Start by cloning the repository
```bash
git clone git@github.com:mrochk/pylob.git
cd pylob
```

To run the tests you can use
```bash
make test
# or
python3 -m unittest discover test
```

***

*Lines count:*
```
   92 pylob/engine/engine.py
    1 pylob/engine/__init__.py
   13 pylob/utils/utils.py
    1 pylob/utils/__init__.py
   56 pylob/order/params.py
    1 pylob/order/__init__.py
  161 pylob/order/order.py
   47 pylob/enums/enums.py
    1 pylob/enums/__init__.py
   58 pylob/orderbook/result.py
  217 pylob/orderbook/orderbook.py
    1 pylob/orderbook/__init__.py
   20 pylob/consts/consts.py
    1 pylob/consts/__init__.py
  119 pylob/limit/limit.py
    1 pylob/limit/__init__.py
  149 pylob/side/side.py
    1 pylob/side/__init__.py
    4 pylob/__init__.py
  944 total
```

***

*NOTE: LLMs are sometimes used for writing tests.*

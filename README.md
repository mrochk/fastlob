# `pylob` | Python Limit-Order-Book
**Fast &amp; minimalist limit-order-book (LOB) implementation in pure Python.**

*Package currently in development, not usable yet.*

The goal is to build an efficient, clean and easy to use package for whoever needs to be able to quickly run a limit order-book in their Python project. We aim to keep the API minimalist and simple, while having reasonable performances (for a pure Python implementation). We intend the final project to contain no more than around 1000 lines of code.

We implement three types of orders: FOK, GTC and GTD. Every order is defined as a limit order, but will be executed as market order if its price matches the best bid or ask limit in the book.

<a href="TODO.md">TODO</a>

<img src="ss.png" width=400>

*Lines count (as of 13-02-2025):*
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

*NOTE: LLMs are used for writing some tests.*

# `pylob` | Python Limit-Order-Book
Fast &amp; minimalist limit-order-book (LOB) implementation in pure Python.

*Package currently in development, not usable yet.*

<a href="TODO.md">TODO</a>

***The goal is to build an efficient, clean and easy to use package for whoever needs to be able to quickly run a limit order-book in their Python project. We aim to keep the API minimalist and simple, while having reasonable performances (for a pure Python implementation). We intend the final project to contain around 1000 lines (of code).***

***We implement three types of orders: FOK, GTC and GTD. Every order is defined as a limit order, but will be executed as market order if its price matches the best bid or ask limit in the book.*** 

<img src="ss.png" width=400>

*Lines count (as of 13-02-2025):*
```
   86 pylob/engine/engine.py
    1 pylob/engine/__init__.py
   23 pylob/utils/utils.py
    1 pylob/utils/__init__.py
   52 pylob/order/params.py
    1 pylob/order/__init__.py
  161 pylob/order/order.py
   47 pylob/enums/enums.py
    1 pylob/enums/__init__.py
   58 pylob/orderbook/result.py
  202 pylob/orderbook/orderbook.py
    1 pylob/orderbook/__init__.py
   11 pylob/consts/consts.py
    1 pylob/consts/__init__.py
  119 pylob/limit/limit.py
    1 pylob/limit/__init__.py
  149 pylob/side/side.py
    1 pylob/side/__init__.py
    4 pylob/__init__.py
  920 total
```


*NOTE: LLMs are used for writing some tests.*

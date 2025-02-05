# `pylob` | Python Limit Order-book
Fast &amp; minimalist limit order-book (LOB) implementation in pure Python.

*Package currently in development.*

TODO:
- [ ] Write benchmarks that will be used to guide development.
- [ ] Decide for the each modules responsibilities, especially in terms for safety checking.
- [ ] Implement the three types of orders.

The goal is to build an efficient, clean and easy to use package for whoever needs to be able to quickly run a limit order-book in their Python project. We aim to keep the API minimalist and simple, while having reasonable performances (for a pure Python implementation). We intend the final project to not exceed 1000 lines of code. 

We implement three types of orders: FOK, GTC and GTD. Every order is defined as a limit order, but will be executed as market order if its price matches the best bid or ask limit in the book.  

*NOTE: LLMs are used for writing some tests.*

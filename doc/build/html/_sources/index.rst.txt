.. fastlob documentation master file, created by
   sphinx-quickstart on Mon Apr 21 14:20:22 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/fastlob-logo.png
  :width: 800
  :alt: Logo

.. raw:: html

   <!--<div style="text-align: center;"><h1><code>fastlob</code></h1></div>-->
   <div style="text-align: center;">Fast & minimalist limit-order-book implementation in Python, with almost no dependencies.</div>
   <br>
   <div style="text-align: center;"><a href="https://github.com/mrochk/fastlob">GitHub</a>  |  <a href="https://pypi.org/project/fastlob">PyPI</a></div>

|

*Package currently in development.*

*For now, I have decided to keep this project in pure Python (no interfacing with C/C++), but that may change in the future.*

----------------

.. raw:: html

   <div style="text-align: center;"><h3>Quickstart</h3></div>

|

To install the package you can install it easily using pip:

.. code-block:: bash

   pip install fastlob

Otherwise, one can build the project from source:

.. code-block:: bash

   git clone git@github.com:mrochk/fastlob.git
   cd fastlob
   pip install -r requirements.txt
   pip install .

----------------

.. raw:: html

   <div style="text-align: center;"><h3>Examples</h3></div>

|

.. code-block:: python
   :linenos:
   :caption: Placing a limit GTD order and getting its status.

   import time, logging

   from fastlob import (
      Orderbook, 
      OrderParams, 
      OrderSide, 
      OrderType,
   )

   logging.basicConfig(level=logging.INFO) # maximum logging

   with Orderbook(name='example') as lob: # init and start lob in cm

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
      status, quantity_left = lob.get_status(result.orderid())
      print(f'Current order status: {status.name}, quantity left: {quantity_left}.\n')

      lob.render() # pretty-print the book state

   # if lob not started using context manager, must call lob.stop() before terminating

|

.. code-block:: python
   :linenos:
   :caption: Run a market simulation using various distributions.

   import random, time, os
   from scipy import stats

   from fastlob import (
      Orderbook, 
      OrderParams, 
      OrderSide,
   )

   def generate_orders(T: int, midprice: float) -> list:
      '''
      A function for generating random batches of orders around a certain midprice.
      '''
      result = []
    
      for _ in range(T):
    
         # how many limit orders to place
         n_ask_limits = stats.poisson.rvs(500)
         n_bid_limits = stats.poisson.rvs(500)
    
         ask_limits_price = stats.expon.rvs(loc=midprice, scale=1, size=n_ask_limits)
         bid_limits_price = -stats.expon.rvs(loc=midprice, scale=1, size=n_bid_limits) + 2*midprice
    
         ask_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_ask_limits)
         bid_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_bid_limits)
    
         ask_limits_params = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_limits_price, ask_limits_quantities)]
         bid_limits_params = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_limits_price, bid_limits_quantities)]
    
         # how many market orders to place
         n_markets = stats.poisson.rvs(100)
    
         markets_price = stats.norm.rvs(loc=midprice, scale=2, size=n_markets)
         markets_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_markets)
         markets_bid_or_ask = [random.choice((OrderSide.BID, OrderSide.ASK)) for _ in range(n_markets)]
    
         markets_params = [OrderParams(s, p, q) for (s, p, q) in zip(markets_bid_or_ask, markets_price, markets_quantities)]
    
         orders = ask_limits_params + bid_limits_params + markets_params
         random.shuffle(orders)
         result.append(orders)
        
      return result

   def simulate(orders: list, speed: float) -> None:
      with Orderbook('simulation') as ob:

         for o in orders:
            ob.process_many(o)
            print(); ob.render()
            time.sleep(speed)
            os.system('clear')

   # main:
   orders = generate_orders(10, 100)
   simulate(orders, 0.5)

|

.. code-block:: python
   :linenos:
   :caption: Running the lob using historical price levels data. 

   from fastlob import (
      Orderbook, 
      OrderParams, 
      OrderSide,
   )

   # initial state of the book
   snapshot = {
      'bids': [ # bid side
         (98.78, 11.56), # (price, quantity)
         (95.65, 67.78), (94.23, 56.76),
         (93.23, 101.59), (90.03, 200.68),
      ],
      'asks': [ # ask side
         (99.11, 12.87), # (price, quantity)
         (100.89, 45.87), (101.87, 88.56),
         (103.78, 98.77), (105.02, 152.43),
      ]
   }

   # list of successive (price, quantity) updates to apply
   updates = [
      # update 1
      {
         'bids': [
            (99.07, 10.01), (95.65, 79.78),
            (93.23, 89.59), (90.03, 250.68),
         ],
         'asks': [(99.11, 5.81)]
      },

      # update 2
      {
         'bids': [(99.07, 0.00), (98.78, 3.56), (79.90, 100.56)],
         'asks': [(103.78, 90.77), (105.02, 123.43)]
      },
    
      # update 3     
      {
      'bids': [
         (98.78, 11.56), (95.65, 67.78), (94.23, 56.76),
         (93.23, 0.00), (90.03, 0.00), 
         # updates that set qty to 0 also delete the limit
         # if no other order sits there
      ],
      'asks': [
         (99.11, 0.00), (100.89, 0.00),
         (101.87, 0.00), (103.78, 1.23),
         (105.02, 152.43),
      ]}]

    # initialize order-book from snapshot
    ob = Orderbook.from_snapshot(snapshot, start=True)
    ob.load_updates(updates) # load updates to be able to call step()

    ob.render()

    ob.step() # apply first update
    ob.render()

    # even tho we use historical data,
    # can still place a manual order between updates
    ob(OrderParams(OrderSide.BID, 99.07, 1.98))

    ob.step() # apply second update
    ob.render()

    ob.step() # apply third update
    ob.render()

    ob.stop()

----------------

.. raw:: html

   <div style="text-align: center;"><h3>API Reference</h3></div>

|

.. toctree::
   :maxdepth: 1
   :name: apiref
   :caption: API Reference

   api/lob
   api/engine
   api/side
   api/limit
   api/order
   api/result
   api/enums
   api/consts
   api/utils

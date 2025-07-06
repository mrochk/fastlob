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

*This package is still being developed, bugs are expected.*

*This is the very first version of the project, the idea was to have a working, correct and clean single-threaded version before making it fast. The next step is to rewrite the core parts in a faster and concurrent fashion.*

*For now, I have decided to keep it written only in Python (no interfacing with C/C++), but that may change in the future.*

----------------

.. raw:: html

   <div style="text-align: center;"><h3>Quickstart</h3></div>

|

To install the package you can either install it using pip:

.. code-block:: bash

   pip install fastlob

Otherwise, you can build the project from source:

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
   :caption: Placing a limit GTD order and getting his status.

   import time, logging
   from fastlob import Orderbook, OrderParams, OrderSide, OrderType

   logging.basicConfig(level=logging.INFO) # set maximum logging level 

   lob = Orderbook(name='ABCD', start=True) # create a lob an start it

   # create an order
   params = OrderParams(
       side=OrderSide.BID,
       price=123.32,
       quantity=3.4,
       otype=OrderType.GTD, 
       expiry=time.time() + 120 # order will expire in two minutes
   )

   result = lob(params); assert result.success() # place order

   status, qty_left = lob.get_status(result.orderid()) # query status of order
   print(f'Current order status: {status.name}, quantity left: {qty_left}.\n')

   lob.render() # pretty-print the lob 

   lob.stop() # stop background processes

|

.. code-block:: python
   :linenos:
   :caption: Simulate the LOB using various distributions.

   import random, time, os
   from scipy import stats

   from fastlob import Orderbook, OrderParams, OrderSide

   def generate_orders(T: int, midprice: float):
      result = list()
    
      for _ in range(T):
    
         n_ask_limits = stats.poisson.rvs(500)
         n_bid_limits = stats.poisson.rvs(500)
    
         ask_limits_price = stats.expon.rvs(loc=midprice, scale=1, size=n_ask_limits)
         bid_limits_price = -stats.expon.rvs(loc=midprice, scale=1, size=n_bid_limits) + 2*midprice
    
         ask_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_ask_limits)
         bid_limits_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_bid_limits)
    
         ask_limits_params = [OrderParams(OrderSide.ASK, p, q) for (p, q) in zip(ask_limits_price, ask_limits_quantities)]
         bid_limits_params = [OrderParams(OrderSide.BID, p, q) for (p, q) in zip(bid_limits_price, bid_limits_quantities)]
    
         n_markets = stats.poisson.rvs(100)
    
         markets_price = stats.norm.rvs(loc=midprice, scale=2, size=n_markets)
         markets_quantities = stats.uniform.rvs(loc=1, scale=100, size=n_markets)
         markets_bid_or_ask = [random.choice((OrderSide.BID, OrderSide.ASK)) for _ in range(n_markets)]
    
         markets_params = [OrderParams(s, p, q) for (s, p, q) in zip(markets_bid_or_ask, markets_price, markets_quantities)]
    
         orders = ask_limits_params + bid_limits_params + markets_params
         random.shuffle(orders)
        
         result.append(orders)
        
      return result

   def simulate(orders: list, speed: float):
      ob = Orderbook('Simulation')
      ob.start()

      for o in orders:
         ob.process_many(o)
         print()
         ob.render()
         time.sleep(speed)
         os.system('clear')
        
      ob.stop()

   orders = generate_orders(10, 100)
   simulate(orders, 0.5)

|

.. code-block:: python
   :linenos:
   :caption: Use historical data. 

   from fastlob import Orderbook, OrderParams, OrderSide

   snapshot = {
      'bids': [
         (98.78, 11.56),
         (95.65, 67.78),
         (94.23, 56.76),
         (93.23, 101.59),
         (90.03, 200.68),
      ],
      'asks': [
         (99.11, 12.87),
         (100.89, 45.87),
         (101.87, 88.56),
         (103.78, 98.77),
         (105.02, 152.43),
      ]
   }

   updates = [
      # update 1
      {
      'bids': [
         (99.07, 10.01),
         (95.65, 79.78),
         (93.23, 89.59),
         (90.03, 250.68),
      ],
      'asks': [
         (99.11, 5.81),
      ]},

      # update 2
      {
      'bids': [
         (99.07, 0.00),
         (98.78, 3.56),
         (79.90, 100.56),
      ],
      'asks': [
         (103.78, 90.77),
         (105.02, 123.43),
      ]},
    
      # update 3     
      {
      'bids': [
         (98.78, 11.56),
         (95.65, 67.78),
         (94.23, 56.76),
         (93.23, 0.00),
         (90.03, 0.00),
      ],
      'asks': [
         (99.11, 0.00),
         (100.89, 0.00),
         (101.87, 0.00),
         (103.78, 1.23),
         (105.02, 152.43),
      ]}]

    ob = Orderbook.from_snapshot(snapshot, start=True)
    ob.load_updates(updates)

    ob.render()

    ob.step()
    ob.render()

    ob(OrderParams(OrderSide.BID, 99.07, 1.98))

    ob.step()
    ob.render()

    ob.step()
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

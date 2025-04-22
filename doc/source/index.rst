.. fastlob documentation master file, created by
   sphinx-quickstart on Mon Apr 21 14:20:22 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/fastlob-logo.png
  :width: 800
  :alt: Logo

.. raw:: html

   <!--<div style="text-align: center;"><h1><code>fastlob</code></h1></div>-->
   <div style="text-align: center;">Fast & minimalist limit-order-book implementation in pure Python. This package can be used for both live order processing and simulating historical high-frequency market data.</div>
   <br>
   <div style="text-align: center;"><a href="https://github.com/mrochk/fastlob">GitHub</a>  |  <a href="https://pypi.org/project/fastlob">PyPI</a></div>

|

*This package is still being developed, bugs are expected. Do not use in production.*

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

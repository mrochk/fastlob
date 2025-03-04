import unittest
from hypothesis import given, strategies as st

from fastlob import OrderBook, OrderSide, OrderParams, todecimal
from fastlob.enums import OrderStatus
from fastlob.orderbook.result import MarketResult
from fastlob.consts import MIN_VALUE, MAX_VALUE

askprice = st.decimals(min_value=MIN_VALUE + 12, max_value=MAX_VALUE-10, allow_infinity=False, allow_nan=False)
valid_qty = st.decimals(min_value=MIN_VALUE, max_value=MAX_VALUE, allow_infinity=False, allow_nan=False)

def get_bidprice(askprice): return askprice - 1

class TestLimitOrders(unittest.TestCase):
    def setUp(self, askprice=1000): 
        self.ob = OrderBook('TestMarketOrders')

        bidprice = get_bidprice(askprice)

        self.ob.process_one(OrderParams(OrderSide.BID, bidprice, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, bidprice - 10, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, bidprice, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, bidprice - 10, 200))

        self.ob.process_one(OrderParams(OrderSide.ASK, askprice, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, askprice + 10, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, askprice, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, askprice+10, 200))

        ''' Orderbook:
        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''

    '''
    - market order partially fills one
    - market order fully fills one
    - market order fully fills one + partially the next
    - market order fully fills limit
    - market order fully fills limit + partially fills next one
    - market order fully fills limit + fully fills next one
    - market order fully fills limit + fully fills next one + partially fills next
    - market order fully fills 2 limits + fully fills next one + partially fills next

    - market order cant be entirely matched and is placed as a limit order after being partially filled
    '''

    # ask side

    @given(askprice)
    def test_ask_1(self, askprice):
        '''Market ask order partially fills best bid limit order.'''

        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice, 100)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - bidprice | *300* | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 0)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._bid_side.volume(), 700)
        self.assertEqual(self.ob._bid_side.best().volume(), 300)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_bid(), bidprice)

    @given(askprice)
    def test_ask_2(self, askprice):
        '''Market ask order fully fills best bid limit order.'''

        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice, 200)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - bidprice | *200* | *1*
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 1)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._bid_side.volume(), 600)
        self.assertEqual(self.ob._bid_side.best().volume(), 200)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 1)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_bid(), bidprice)

    @given(askprice)
    def test_ask_3(self, askprice):
        '''Market ask order fully fills best bid limit order and partially fills second.'''

        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice, 300)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - bidprice | *100* | *1*
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 1)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._bid_side.volume(), 500)
        self.assertEqual(self.ob._bid_side.best().volume(), 100)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 1)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_bid(), bidprice)

    @given(askprice)
    def test_ask_4(self, askprice):
        '''Market ask order fully fills best bid limit.'''

        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice, 400)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - *
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 2)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._bid_side.volume(), 400)
        self.assertEqual(self.ob._bid_side.best().volume(), 400)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 2)
        self.assertEqual(self.ob._bid_side.best().price(), bidprice - 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_ask_5(self, askprice):
        '''Market ask order fully fills best bid limit and partially fills second limit best order.'''

        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice - 10, 500)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - *
        - bidprice - 10 | *300* | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 2)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._bid_side.volume(), 300)
        self.assertEqual(self.ob._bid_side.best().volume(), 300)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 2)
        self.assertEqual(self.ob._bid_side.best().price(), bidprice - 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_ask_6(self, askprice):
        '''Market ask order fully fills best bid limit and fully fills second limit best order.'''
        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice - 10, 600)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - *
        - bidprice - 10 | *200* | *1*
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 3)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._bid_side.volume(), 200)
        self.assertEqual(self.ob._bid_side.best().volume(), 200)
        self.assertEqual(self.ob._bid_side.best().valid_orders(), 1)
        self.assertEqual(self.ob._bid_side.best().price(), bidprice - 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_ask_7(self, askprice):
        '''Market ask order fully fills bid side.'''
        askprice = todecimal(askprice)
        bidprice = get_bidprice(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.ASK, bidprice - 10, 800)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | 400 | 2
        ----------------------------
        - *
        - *
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 4)
        self.assertEqual(result._limits_matched, 2)

        self.assertTrue(self.ob._bid_side.empty())
        self.assertEqual(self.ob._bid_side.volume(), 0)
        self.assertEqual(self.ob._bid_side.size(), 0)

        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    # bid side

    @given(askprice)
    def test_bid_1(self, askprice):
        '''Market bid order partially fills best ask limit order.'''

        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice, 100)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | *300* | 2
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 0)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._ask_side.volume(), 700)
        self.assertEqual(self.ob._ask_side.best().volume(), 300)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_ask(), askprice)

    @given(askprice)
    def test_bid_2(self, askprice):
        '''Market bid order fully fills best ask limit order.'''

        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice, 200)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | *200* | *1*
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 1)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._ask_side.volume(), 600)
        self.assertEqual(self.ob._ask_side.best().volume(), 200)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 1)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_ask(), askprice)

    @given(askprice)
    def test_bid_3(self, askprice):
        '''Market bid order fully fills best ask limit order and partially fills second.'''

        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice, 300)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - askprice | *100* | *1*
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 1)
        self.assertEqual(result._limits_matched, 0)
        self.assertEqual(self.ob._ask_side.volume(), 500)
        self.assertEqual(self.ob._ask_side.best().volume(), 100)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 1)
        self.assertTupleEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
        self.assertEqual(self.ob.best_ask(), askprice)

    @given(askprice)
    def test_bid_4(self, askprice):
        '''Market bid order fully fills best ask limit.'''

        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice, 400)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | 400 | 2
        - *
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 2)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._ask_side.volume(), 400)
        self.assertEqual(self.ob._ask_side.best().volume(), 400)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 2)
        self.assertEqual(self.ob._ask_side.best().price(), askprice + 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_bid_5(self, askprice):
        '''Market bid order fully fills best ask limit and partially fills second limit best order.'''

        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice + 10, 500)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | *300* | 2
        - *
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 2)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._ask_side.volume(), 300)
        self.assertEqual(self.ob._ask_side.best().volume(), 300)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 2)
        self.assertEqual(self.ob._ask_side.best().price(), askprice + 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_bid_6(self, askprice):
        '''Market ask order fully fills best bid limit and fully fills second limit best order.'''
        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice + 10, 600)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - askprice + 10 | *200* | *1*
        - *
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 3)
        self.assertEqual(result._limits_matched, 1)
        self.assertEqual(self.ob._ask_side.volume(), 200)
        self.assertEqual(self.ob._ask_side.best().volume(), 200)
        self.assertEqual(self.ob._ask_side.best().valid_orders(), 1)
        self.assertEqual(self.ob._ask_side.best().price(), askprice + 10)
        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))

    @given(askprice)
    def test_bid_7(self, askprice):
        '''Market bid order fully fills bid side.'''
        askprice = todecimal(askprice)
        self.setUp(askprice)

        order = OrderParams(OrderSide.BID, askprice + 10, 800)
        result : MarketResult = self.ob.process_one(order)

        ''' 
        Expected:

        - *
        - *
        ----------------------------
        - bidprice | 400 | 2
        - bidprice - 10 | 400 | 2
        '''
        
        self.assertTrue(result.success())
        self.assertEqual(result._orders_matched, 4)
        self.assertEqual(result._limits_matched, 2)

        self.assertTrue(self.ob._ask_side.empty())
        self.assertEqual(self.ob._ask_side.volume(), 0)
        self.assertEqual(self.ob._ask_side.size(), 0)

        self.assertEqual(self.ob.get_order_status(result.order_id()), (OrderStatus.FILLED, 0))
import unittest
import random

from pylob import OrderBook, OrderSide, OrderParams
from pylob.enums import OrderStatus
from pylob.consts import MIN_VALUE, MAX_VALUE
from pylob.orderbook.result import MarketResult

class TestLimitOrders(unittest.TestCase):
    def setUp(self): 
        self.ob = OrderBook('TestMarketOrders')

        self.ob.process_one(OrderParams(OrderSide.BID, 1400, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, 1300, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, 1400, 200))
        self.ob.process_one(OrderParams(OrderSide.BID, 1300, 200))

        self.ob.process_one(OrderParams(OrderSide.ASK, 1500, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, 1600, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, 1500, 200))
        self.ob.process_one(OrderParams(OrderSide.ASK, 1600, 200))

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

    def test_ask_1(self):
        order = OrderParams(OrderSide.ASK, 1400, 100)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 0)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.bid_side.volume(), 700)
        self.assertEqual(self.ob.bid_side.best().volume(), 300)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 2)

    def test_ask_2(self):
        order = OrderParams(OrderSide.ASK, 1400, 200)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 1)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.bid_side.volume(), 600)
        self.assertEqual(self.ob.bid_side.best().volume(), 200)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 1)

    def test_ask_3(self):
        order = OrderParams(OrderSide.ASK, 1400, 300)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 1)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.bid_side.volume(), 500)
        self.assertEqual(self.ob.bid_side.best().volume(), 100)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 1)

    def test_ask_4(self):
        order = OrderParams(OrderSide.ASK, 1400, 400)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 2)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.bid_side.volume(), 400)
        self.assertEqual(self.ob.bid_side.best().volume(), 400)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.bid_side.best().price(), 1300)

    def test_ask_5(self):
        order = OrderParams(OrderSide.ASK, 1300, 500)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 2)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.bid_side.volume(), 300)
        self.assertEqual(self.ob.bid_side.best().volume(), 300)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.bid_side.best().price(), 1300)

    def test_ask_6(self):
        order = OrderParams(OrderSide.ASK, 1300, 600)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 3)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.bid_side.volume(), 200)
        self.assertEqual(self.ob.bid_side.best().volume(), 200)
        self.assertEqual(self.ob.bid_side.best().valid_orders(), 1)
        self.assertEqual(self.ob.bid_side.best().price(), 1300)

    def test_ask_7(self):
        order = OrderParams(OrderSide.ASK, 1300, 800)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 4)
        self.assertEqual(result.limits_filled, 2)
        self.assertEqual(self.ob.bid_side.volume(), 0)
        self.assertEqual(self.ob.bid_side.size(), 0)

    # bid side

    def test_bid_1(self):
        order = OrderParams(OrderSide.BID, 1500, 100)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 0)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.ask_side.volume(), 700)
        self.assertEqual(self.ob.ask_side.best().volume(), 300)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 2)

    def test_bid_2(self):
        order = OrderParams(OrderSide.BID, 1500, 200)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 1)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.ask_side.volume(), 600)
        self.assertEqual(self.ob.ask_side.best().volume(), 200)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 1)

    def test_bid_3(self):
        order = OrderParams(OrderSide.BID, 1500, 300)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 1)
        self.assertEqual(result.limits_filled, 0)
        self.assertEqual(self.ob.ask_side.volume(), 500)
        self.assertEqual(self.ob.ask_side.best().volume(), 100)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 1)

    def test_bid_4(self):
        order = OrderParams(OrderSide.BID, 1500, 400)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 2)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.ask_side.volume(), 400)
        self.assertEqual(self.ob.ask_side.best().volume(), 400)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.ask_side.best().price(), 1600)

    def test_bid_5(self):
        order = OrderParams(OrderSide.BID, 1600, 500)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 2)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.ask_side.volume(), 300)
        self.assertEqual(self.ob.ask_side.best().volume(), 300)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 2)
        self.assertEqual(self.ob.ask_side.best().price(), 1600)

    def test_bid_6(self):
        order = OrderParams(OrderSide.BID, 1600, 600)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 3)
        self.assertEqual(result.limits_filled, 1)
        self.assertEqual(self.ob.ask_side.volume(), 200)
        self.assertEqual(self.ob.ask_side.best().volume(), 200)
        self.assertEqual(self.ob.ask_side.best().valid_orders(), 1)
        self.assertEqual(self.ob.ask_side.best().price(), 1600)

    def test_bid_7(self):
        order = OrderParams(OrderSide.BID, 1600, 800)
        result : MarketResult = self.ob.process_one(order)
        
        self.assertTrue(result.success())
        self.assertEqual(result.orders_filled, 4)
        self.assertEqual(result.limits_filled, 2)
        self.assertEqual(self.ob.ask_side.volume(), 0)
        self.assertEqual(self.ob.ask_side.size(), 0)
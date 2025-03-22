from fastlob import Orderbook, OrderParams, OrderSide
import logging

logging.basicConfig(level=logging.WARNING)

lob = Orderbook()
lob.start()

lob.process_one(OrderParams(OrderSide.BID, 100, 100))
lob.process_one(OrderParams(OrderSide.BID, 110, 100))
lob.process_one(OrderParams(OrderSide.BID, 120, 100))
lob.process_one(OrderParams(OrderSide.BID, 121, 100))
lob.process_one(OrderParams(OrderSide.BID, 121.1, 100))

lob.process_one(OrderParams(OrderSide.ASK, 122, 100))

b = lob.best_bids(7)
print()

for x in b: print(x)

print()

a = lob.best_asks(2)

for x in a: print(x)

lob.stop()
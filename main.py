import fastlob as lob
import logging

logging.basicConfig(level=logging.WARNING)

snapshot = {
    'asks': [
        (100, 10),
        (101, 10),
        (102, 10),
    ],

    'bids': [
        (99, 10),
        (98, 10),
        (97, 10),
    ],
}

updates = [{
    'asks': [
        (100, 11),
        (101, 9),
        (102, 12),
    ],

    'bids': [
        (99, 10),
        (98, 10),
        (97, 10),
    ],
}, {
    'asks': [
        (110, 100),
        (101, 10),
        (102, 10),
    ],

    'bids': [
        (99, 10),
        (98, 0),
        (50, 10),
    ],
}]

ob = lob.Orderbook.from_snapshot(snapshot)

ob.load_updates(updates)

ob.start()

ob.render()

ob.step()

ob.render()

ob.step()

ob(lob.OrderParams(lob.OrderSide.BID, 50, 10))

ob.render()

ob.step()
ob.step()

ob.stop()
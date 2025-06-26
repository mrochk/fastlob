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

if __name__ == '__main__':
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
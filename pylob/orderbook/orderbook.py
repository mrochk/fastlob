from sortedcollections import SortedDict

class OrderBook:
    def __init__(self):
        self.asks = SortedDict()
        self.bids = SortedDict(lambda x: -x)
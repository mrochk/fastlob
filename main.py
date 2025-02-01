import pylob
import pylob.order

if __name__ == '__main__':

    o = pylob.order.AskOrder(
        price=1000.987,
        quantity=98765.8765,
        type=pylob.order.OrderType.FOK
    )

    print(o)
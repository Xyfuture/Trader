import random

from trader.Order import Order


class RandomStrategy:
    def __init__(self, parameter):
        pass

    def generate_signal(self, data):
        r = random.random()
        if r < 0.3:
            return Order(-1)
        elif r > 0.7:
            return Order(1)
        return Order()
        # return Order(1)
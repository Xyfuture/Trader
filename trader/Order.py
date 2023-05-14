import asyncio


class Order:
    def __init__(self, direction=0, proportion=0.2, instrument=None, order_type=None, order_source='strategy'
                 , size=None,
                 take_profit_price=0, stop_loss_price=0, **kwargs):
        self.instrument = instrument
        self.direction = direction
        self.proportion = proportion
        self.order_type = order_type
        self.size = size

        self.take_profit_price = take_profit_price
        self.stop_loss_price = stop_loss_price

        self.place_status = "unplaced" # placed, failed, successful,trying,
        self.order_source = order_source  # strategy take_profit stop_loss

        self.kwargs = kwargs

    def __str__(self):
        _str = f"Order> Instrument:{self.instrument} direction:{self.direction} order_type:{self.order_type} size:{self.size}"
        return _str

    def __repr__(self):
        print(self)


class AsyncOrderTask:
    def __init__(self, order):
        self.order = order
        self.event = asyncio.Event()
        self.ret = False

    async def wait(self)->bool:
        await self.event.wait()
        return self.ret

    def set(self,ret:bool):
        self.ret = ret
        self.event.set()
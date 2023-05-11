

class Order:
    def __init__(self,direction=0,instrument=None,order_type=None,size=None,**kwargs):
        self.instrument = instrument
        self.direction = direction
        self.order_type = order_type
        self.size = size

        self.kwargs = kwargs

    def __str__(self):
        _str = f"Order> Instrument:{self.instrument} direction:{self.direction} order_type:{self.order_type} size:{self.size}"
        return _str

    def __repr__(self):
        print(self)





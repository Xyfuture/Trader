from trader.Broker import Broker
from trader.Order import Order


class OrderManager:
    def __init__(self, broker: Broker, config):
        self.broker = broker
        self.config = config
        self.instrument = config['instrument']
        self.risk_strategy = config['risk_strategy']

    def place_order(self, order: Order):
        order = self.complete_order(order)

        if self.check_order(order):
            self.broker.place_order(order)
            print(f"{order}\nhas been placed to exchange")
        else:
            print(f"{order}\n passed by bot")

    async def order_risk_control(self):
        pass

    def size_order(self, order) -> Order:
        # 选中策略
        # 计算容量
        # allin 发射
        if order.direction == 1:
            # long trade
            currency = order.instrument.split('-')[1]
            balance = self.broker.get_balance(currency)
            last_price = self.broker.fetchTicker(self.instrument)['last']
            amount = (balance / last_price) * 0.99
            if self.risk_strategy == 'allin':
                order.size = amount
            else:
                raise "Not implement"
        elif order.direction == -1:
            currency = order.instrument.split('-')[0]
            balance = self.broker.get_balance(currency)
            if self.risk_strategy == 'allin':
                order.size = balance
            else:
                raise "Not implement"

        return order

    def complete_order(self, order) -> Order:
        order.instrument = self.instrument

        if not order.order_type:
            order.order_type = 'market'
        order = self.size_order(order)
        return order

    def check_order(self, order) -> bool:
        if order.instrument is not None and order.direction != 0 and order.size != 0:
            if order.order_type in ['market']:
                return True
        return False

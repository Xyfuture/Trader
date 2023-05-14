from trader.Broker import Broker
from trader.Order import Order, AsyncOrderTask
import queue
import asyncio


class OrderManager:
    def __init__(self, broker: Broker, config):
        self.broker = broker
        self.config = config
        self.instrument = config['instrument']
        self.risk_strategy = config['risk_strategy']

        self.all_orders = []
        self.pending_orders = asyncio.Queue()  # wait for trade
        self.under_risk_orders = []  # unsold buy orders

    async def process_order(self,order:Order):
        pass

    async def place_order(self, order: Order) -> bool:
        order_task = AsyncOrderTask(order)
        await self.pending_orders.put(order_task)
        ret = await order_task.wait()
        return ret

    async def _place_order(self, order: Order) -> bool:
        order = self.fill_order(order)

        if self.check_order(order):
            self.broker.place_order(order)
            print(f"{order}\nhas been placed to exchange")
        else:
            print(f"{order}\npassed by bot")

        return True

    async def order_risk_control(self):
        # loop check order risk
        while True:
            if self.under_risk_orders:
                last_price = self.broker.fetchTicker(self.instrument)['last']
                risk_orders = [order for order in self.under_risk_orders if
                               order.stop_loss_price > last_price or order.take_profit_price < last_price]

                for order in risk_orders:
                    source = "take_profit" if order.take_profit_price > last_price else "stop_loss"
                    new_order = Order(direction=-1, size=order.size, order_source=source)
                    ret = await self.place_order(new_order)

                    if ret:
                        self.under_risk_orders.remove(order)

            await asyncio.sleep(60)

    def fill_order(self, order) -> Order:
        def strategy_size_order(order) -> Order:
            # 选中策略
            # 计算容量
            # allin 发射
            if order.direction == 1:
                # long trade
                currency = order.instrument.split('-')[1]
                balance = self.broker.get_balance(currency)
                buy_balance = balance * order.proportion
                if 0 < buy_balance < balance:
                    last_price = self.broker.fetchTicker(self.instrument)['last']
                    amount = (buy_balance / last_price)
                    order.size = amount
                else:
                    order.size = 0

            elif order.direction == -1:
                if not self.under_risk_orders.empty():
                    cur_order = self.under_risk_orders.get()
                    order.size = cur_order.size
                else:
                    order.size = 0

            return order

        # basic info
        order.instrument = self.instrument
        if not order.order_type:
            order.order_type = 'market'

        if order.order_source == 'strategy':
            order = strategy_size_order(order)
        elif order.order_source == 'take_profit':
            pass
        elif order.order_source == 'stop_loss':
            pass
        else:
            raise "not implement"

        return order

    def check_order(self, order) -> bool:
        if order.instrument is not None and order.direction != 0 and order.size != 0:
            if order.order_type in ['market']:
                return True
        return False

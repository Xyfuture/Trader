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

        self.all_orders = []  # managed by place order
        # self.pending_orders = asyncio.Queue()  # wait for trade
        self.under_risk_orders = []  # unsold buy orders

    async def process_order(self, order: Order):
        order = self.fill_order(order)


    async def place_order(self, order: Order) -> bool:
        self.all_orders.append(order)

        order_task = AsyncOrderTask(order)
        await self.pending_orders.put(order_task)

        ret = await order_task.wait()
        return ret

    async def _place_order(self, order: Order):
        # pass
        while True:
            order_task: AsyncOrderTask = await self.pending_orders.get()

            order = order_task.order
            if self.check_order(order):
                self.broker.place_order(order)
                print(f'{order}\nhas benn placed to exchange')
            else:
                print(f'{order}\nignored by bot')

            order_task.set(True)  # finish

        # order = self.fill_order(order)
        #
        # if self.check_order(order):
        #     self.broker.place_order(order)
        #     print(f"{order}\nhas been placed to exchange")
        # else:
        #     print(f"{order}\npassed by bot")
        #
        # return True

    async def order_risk_control(self):  # take profit, stop loss
        # loop check order risk
        while True:
            if self.under_risk_orders:
                last_price = self.broker.fetchTicker(self.instrument)['last']
                risk_orders = [order for order in self.under_risk_orders if
                               order.stop_loss_price > last_price or order.take_profit_price < last_price]

                for order in risk_orders:
                    source = "take_profit" if order.take_profit_price > last_price else "stop_loss"
                    sell_order = Order(direction=-1, size=order.size, order_source=source)
                    sell_order = self.fill_order(sell_order)
                    ret = await self.place_order(sell_order)

                    if ret:
                        self.under_risk_orders.remove(order)

            await asyncio.sleep(60)

    def fill_order(self, order) -> Order:
        def strategy_size_order(order: Order) -> Order:
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
                # shot trade
                # sell all
                instrument = order.instrument.split('-')[0]
                balance = self.broker.get_balance(instrument)

                order.size = balance

            return order

        # basic info
        order.instrument = self.instrument
        if not order.order_type:
            order.order_type = 'market'

        # how to fill order
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

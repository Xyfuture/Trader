import asyncio
from time import sleep

from trader.Broker import Broker
from trader.DataManager import DataManager
from trader.OrderManager import OrderManager
from trader.Strategy import BaseStrategy
import yaml
import re


class TradeBot:
    def __init__(self, config_path, broker_config_path, strategy_class=BaseStrategy):

        with open(config_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        with open(broker_config_path, 'r') as f:
            broker_config = yaml.load(f, Loader=yaml.FullLoader)

        self.config = self.complete_config(config)
        self.broker_config = broker_config

        self.broker = Broker(broker_config)

        self.data_manager = DataManager(self.broker, self.config)
        self.strategy = strategy_class(self.config['parameter'])

        self.order_manager = OrderManager(self.broker, self.config)

        self.interval = self.config['interval']

    def complete_config(self, config) -> dict:
        default_config = {
            "interval": '1h',
            'period': 100,
            'instrument': 'BTC-USDT',
            'parameter': None,
            'risk_strategy': 'allin',
            'risk_control_interval': 60 # seconds

        }
        for k, v in config.items():
            default_config[k] = v

        return default_config

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        tasks = [self.strategy_loop(), self.order_manager.order_risk_control()]
        await asyncio.gather(*tasks)

    async def strategy_loop(self):
        while True:
            self.run_once()
            await asyncio.sleep(self.get_interval_seconds(self.interval))

    def run_once(self):
        print("Bot Working ...")
        history_data = self.data_manager.fetch_history_data()
        print("Trade Data Fetched!")
        order = self.strategy.generate_signal(history_data)
        print(f"Signal Generated> Order Direction:{order.direction}")
        self.order_manager.process_order(order)
        print("Bot Sleeping ...\n")

    def get_interval_seconds(self, interval):
        match = re.match(r'^(\d+)([smhd])$', interval)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit == 's':
                return num
            elif unit == 'm':
                return num * 60
            elif unit == 'h':
                return num * 3600
            elif unit == 'd':
                return num * 86400
        else:
            raise ValueError('Invalid duration string')

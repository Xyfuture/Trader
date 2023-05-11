import pandas as pd

from trader.Broker import Broker


class DataManager:
    def __init__(self, broker: Broker, config):
        self.broker = broker
        self.config = config

        self.instrument = config['instrument']
        self.interval = config['interval']
        self.period = config['period']

    def fetch_history_data(self) -> pd.DataFrame:
        raw_data = self.broker.fetchOHLCV(
            self.instrument, timeframe=self.interval, limit=self.period
        )
        data = pd.DataFrame(
            raw_data, columns=["time", "Open", "High", "Low", "Close", "Volume"]
        ).set_index("time")
        data.index = pd.to_datetime(data.index, unit="ms")
        return data

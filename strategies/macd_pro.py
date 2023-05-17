import pandas as pd
import numpy as np
import talib

from trader.Order import Order


class MACDPro:
    def __init__(self,parameters):
        self.name = "MACD PRO For BTC"
        self.params = parameters
        # self.instrument = instrument

        self.fast_period = parameters['fast_period']
        self.slow_period = parameters['slow_period']
        self.signal_period = parameters['signal_period']
        self.threshold = parameters['threshold']
        self.exit_period = parameters['exit_period']
        self.proportion = parameters['proportion']
        self.take_profit_level = parameters['take_profit_level']
        self.stop_loss_level = parameters['stop_loss_level']



    def generate_signal(self,data:pd.DataFrame)->Order:
        # 仅使用收盘价进行处理
        market_vector = data['Close'].to_numpy()

        log_price = np.log(market_vector)
        MACD, Signal, _ = talib.MACD(
            log_price,
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )
        MACD_diff = MACD.copy()
        # MACD_diff = np.diff(MACD)
        MACD_diff[1:] = MACD_diff[1:] - MACD_diff[:-1]
        MACD_diff[0] = np.nan

        AVG = talib.SMA(log_price, timeperiod=self.exit_period)
        signal = np.zeros(shape=(len(MACD),), dtype=np.int32)

        # 策略核心：
        # 1) MACD金叉时进场；排除MACD波动太小的干扰
        # 2) 趋势向下且均线死叉时快速离场，及时止损
        for i in range(max(self.fast_period, self.slow_period, self.exit_period), len(market_vector)):
            if np.abs(MACD_diff[i]) > self.threshold and MACD[i] > Signal[i] and MACD[i - 1] <= Signal[i - 1]:
                signal[i] = 1
            elif AVG[i] <= AVG[i - 1] and log_price[i] < AVG[i] and log_price[i - 1] >= AVG[i - 1]:
                signal[i] = -1

        take_profit = market_vector[-1] * (1+self.take_profit_level)
        stop_loss = market_vector[-1] * (1-self.stop_loss_level)

        if signal[-1] == 1:
            return Order(direction=1,proportion=self.proportion,
                         take_profit_price=take_profit,stop_loss_price=stop_loss)
        elif signal[-1] == -1:
            return Order(direction=-1,proportion=self.proportion,
                         take_profit_price=take_profit,stop_loss_price=stop_loss)

        return Order()

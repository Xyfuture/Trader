from strategies.macd_pro import MACDPro
from strategies.rand import RandomStrategy
from trader.TradeBot import TradeBot

if __name__ == '__main__':
    trader = TradeBot(r'.\config\macd_pro.yaml',r'.\config\ccxt.yaml',MACDPro)
    trader.run()

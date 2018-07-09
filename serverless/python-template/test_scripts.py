from StrategyHandler import AbstractStrategyHandler
from TradingStrategy123 import TradingStrategy123


# def test1():
abh = AbstractStrategyHandler()
d = abh.get_indicator("RSI")
print(d)

ts123 = TradingStrategy123(sns_context={})

ts123.run()
ts123.savf()

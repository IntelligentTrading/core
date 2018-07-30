from abc import ABC

import talib

import numpy as np

# note that all ndarrays must be the same length!
from TA.storages.abstract.ticker import TickerStorage
from TA.storages.data.pv_history import PriceVolumeHistoryStorage


class SMA(ABC):

    def __init__(self):
        pass

    sorted_set_key = "BTC_USDT:poloniex:PriceVolumeHistoryStorage:close_price"




results_dict = PriceVolumeHistoryStorage.query(
    ticker="BTC_USDT",
    exchange="poloniex",
    index="close_price",
    periods=10)

inputs = {
    'open': np.random.random(100),
    'high': np.random.random(100),
    'low': np.random.random(100),
    'close': np.random.random(100),
    'volume': np.random.random(100)
}



# uses close prices (default)
output = talib.SMA(inputs, timeperiod=25)

# uses open prices
output = talib.SMA(inputs, timeperiod=25, price='values')

# uses close prices (default)
upper, middle, lower = talib.BBANDS(inputs, 20, 2, 2)

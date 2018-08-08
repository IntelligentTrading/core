from abc import ABC

import talib

import numpy as np

# note that all ndarrays must be the same length!
from apps.TA.storages.abstract.ticker import TickerStorage
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage
from settings import logger

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]
INDEXES = ['open', 'high', 'low', 'close', 'volume']

class SMA(ABC):

    def __init__(self, *args, **kwargs):
        self.ticker = kwargs['ticker']  # str eg. BTC_USD
        self.exchange = str(kwargs.get('exchange', ""))  # str or int
        self.periods = kwargs.get('periods', 50)

    def get_data(self):
        data = {}
        for index in INDEXES:
            results_dict = PriceVolumeHistoryStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=index,
                periods=self.periods
            )
            logger.debug(results_dict)
            data['index'] = np.array(
                [float(v) for v in results_dict['values']]
            )
        return data

    def __call__(self, *args, **kwargs):
        inputs = self.get_data()
        return talib.SMA(inputs, timeperiod=self.periods)[-1]




# sorted_set_key = "BTC_USDT:poloniex:PriceVolumeHistoryStorage:close_price"

#
# inputs = {
#     'open': np.random.random(100),
#     'high': np.random.random(100),
#     'low': np.random.random(100),
#     'close': np.random.random(100),
#     'volume': np.random.random(100)
# }
#
#
#
# # uses close prices (default)
# output = talib.SMA(inputs, timeperiod=25)
#
# # uses open prices
# output = talib.SMA(inputs, timeperiod=25, price='values')
#
# # uses close prices (default)
# upper, middle, lower = talib.BBANDS(inputs, 20, 2, 2)
#
#
# SMA(ticker="ETH_BTC", exchange="binance", periods=50)

# from apps.TA.storages.indicators.ta_lib_indicator import SMA
import talib
import numpy as np

from apps.TA import PERIODS_1HR, PERIODS_4HR, PERIODS_24HR, HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.subscriber import TickerSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger, PERIODS_LIST

# PERIODS_LIST = list([60,240,1440])

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]

class SMAStorage(IndicatorStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class SMASubscriber(TickerSubscriber):

    classes_subscribing_to = [
        PriceStorage
    ]


    def handle(self, channel, data, *args, **kwargs):
        [ticker, exchange, class_describer, index] = data.split(":")
        # eg. "BLZ_ETH:binance:PriceStorage:close_price"

        if index != 'close_price':
            return

        #todo: this can be refactored into only one query!!
        #todo: after one query for all values, then cut to sizes for horizons and periods
        #todo: also there is some overlap. h=48, p=30 is the same as h=12,p=120

        for horizon in HORIZONS:
            for periods in SMA_LIST:

                results_dict = PriceStorage.query(
                    ticker=ticker,
                    exchange=exchange,
                    index=index,
                    periods_key=None, # PriceStorage not unique to periods by key
                    periods_range=periods*horizon
                )
                logger.debug(results_dict)
                value_array = [float(v) for v in results_dict['values']]
                if len(value_array) > periods*horizon:
                    value_array = value_array[-periods*horizon:0]

                value_np_array = np.array(value_array)

                sma_value = talib.SMA(value_array, timeperiod=len(value_array))[-1]

                new_sma_storage = SMAStorage(ticker=ticker,
                                             exchange=exchange, timestamp=908)


# sorted_set_key = "BTC_USDT:poloniex:PriceVolumeHistoryStorage:close_price"

# note that all ndarrays must be the same length!
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
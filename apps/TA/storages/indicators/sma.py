from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib
import numpy as np

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]


class SmaStorage(IndicatorStorage):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)


class SmaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        """
        now available:
            self.ticker as str
            self.exchange as str
            self.key_suffix as str
            self.timestamp as int
            self.value as str
        """
        # key for PriceStorage like "BLZ_ETH:binance:PriceStorage:close_price"
        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not `close_price` ...ignoring...')
            return

        new_sma_storage = SmaStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        periods_list = []
        for s in SMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        for periods in set(periods_list):

            # todo: this can be refactored into only one query!
            # todo: after one query for all values, then cut to sizes for horizons and periods
            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                periods_range=periods
            )

            logger.debug(results_dict)
            value_array = [float(v) for v in results_dict['values']]
            if len(value_array) > periods:
                value_array = value_array[-periods:0]

            value_np_array = np.array(value_array)

            sma_value = talib.SMA(value_array, timeperiod=len(value_array))[-1]
            logger.debug(f'saving SMA value {sma_value} for {ticker} on {periods} periods')

            new_sma_storage.periods = periods
            new_sma_storage.value = int(float(sma_value))
            new_sma_storage.save()

# sorted_set_key = "BTC_USDT:poloniex:SmaStorage:20"

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

# from apps.TA.storages.indicators.sma import SmaStorage

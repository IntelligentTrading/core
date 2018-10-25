import math
from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

EMA_LIST = [30, 50, 200,]


class EmaStorage(IndicatorStorage):

    # sorted_set_key = "BTC_USDT:poloniex:EmaStorage:30"

    def produce_signal(self):
        pass


class EmaSubscriber(IndicatorSubscriber):

    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        periods_list = []
        for s in EMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        new_ema_storage = EmaStorage(ticker=self.ticker, exchange=self.exchange, timestamp=self.timestamp)
        for periods in set(periods_list):

            close_value_np_array = new_ema_storage.get_denoted_price_array("close_price", periods)
            if not len(close_value_np_array):
                return

            ema_value = talib.EMA(close_value_np_array, timeperiod=periods)[-1]
            if math.isnan(ema_value):
                return
            # # logger.debug(f'savingEma value {ema_value}for {self.ticker} on {periods} periods')


            new_ema_storage.periods = periods
            new_ema_storage.value = float(ema_value)
            new_ema_storage.save()

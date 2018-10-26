from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

TRIMA_LIST = [30,]


class TrimaStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class TrimaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_trima_storage = TrimaStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        periods_list = []
        for s in TRIMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        for periods in set(periods_list):

            close_value_np_array = new_trima_storage.get_denoted_price_array("close_price", periods)

            trima_value = talib.TRIMA(close_value_np_array, timeperiod=periods)[-1]
            # logger.debug(f'savingTrima value {trima_value}for {self.ticker} on {periods} periods')

            new_trima_storage.periods = periods
            new_trima_storage.value = float(trima_value)
            new_trima_storage.save()

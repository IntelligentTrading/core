import math
from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]


class SmaStorage(IndicatorStorage):

    def get_periods_list(self):
        periods_list = []
        for s in SMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])
        return set(periods_list)

    # sorted_set_key = "BTC_USDT:poloniex:SmaStorage:20"

    def compute_value(self, periods: int = 0) -> str:
        periods = periods or self.periods

        value_array = self.get_denoted_price_array("close_price", periods)
        if not len(value_array): return ""

        sma_value = talib.SMA(value_array, timeperiod=periods)[-1]
        if math.isnan(sma_value): return ""

        return str(sma_value)

    def compute_and_save(self) -> bool:
        """

        :return: True if value saved, else False
        """

        if not all([
            self.ticker, self.exchange, self.timestamp, self.periods
        ]):
            raise Exception("missing required values")

        self.value = self.compute_value(self.periods)
        if self.value:
            self.save()
        return bool(self.value)

    def produce_signal(self):
        pass


class SmaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        if not 'close_price' == self.key_suffix:
            logger.debug(f'index {self.key_suffix} is not close_price ...ignoring...')
            return

        new_sma_storage = SmaStorage(ticker=self.ticker, exchange=self.exchange, timestamp=self.timestamp)

        for periods in self.get_periods_list():
            new_sma_storage.periods = periods
            new_sma_storage.compute_and_save()
            # logger.debug(f'savingSMA value {sma_value}for {self.ticker} on {periods} periods')

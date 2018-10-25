from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class UltoscStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class UltoscSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_ultosc_storage = UltoscStorage(ticker=self.ticker,
                                           exchange=self.exchange,
                                           timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 28

            high_value_np_array = new_ultosc_storage.get_denoted_price_array("high_price", periods)
            low_value_np_array = new_ultosc_storage.get_denoted_price_array("low_price", periods)
            close_value_np_array = new_ultosc_storage.get_denoted_price_array("close_price", periods)

            ultosc_value = talib.ULTOSC(high_value_np_array, low_value_np_array, close_value_np_array,
                                        timeperiod1=horizon * 7, timeperiod2=horizon * 14, timeperiod3=horizon * 28)[-1]
            # logger.debug(f'savingUltosc value {ultosc_value} for {self.ticker} on {periods} periods')

            new_ultosc_storage.periods = periods
            new_ultosc_storage.value = float(ultosc_value)
            new_ultosc_storage.save()

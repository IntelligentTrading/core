from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class WillrStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class WillrSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_willr_storage = WillrStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 14

            high_value_np_array = new_willr_storage.get_denoted_price_array("high_price", periods)
            low_value_np_array = new_willr_storage.get_denoted_price_array("low_price", periods)
            close_value_np_array = new_willr_storage.get_denoted_price_array("close_price", periods)

            willr_value = talib.WILLR(high_value_np_array, low_value_np_array, close_value_np_array,
                                      timeperiod=horizon*14)[-1]
            # logger.debug(f'savingWillr value {willr_value} for {self.ticker} on {periods} periods')

            new_willr_storage.periods = periods
            new_willr_storage.value = float(willr_value)
            new_willr_storage.save()

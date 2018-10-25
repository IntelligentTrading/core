from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class StochfStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class StochfSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_stochf_storage = StochfStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 5

            high_value_np_array = new_stochf_storage.get_denoted_price_array("high_price", periods)
            low_value_np_array = new_stochf_storage.get_denoted_price_array("low_price", periods)
            close_value_np_array = new_stochf_storage.get_denoted_price_array("close_price", periods)

            fastk, fastd = talib.STOCHF(high_value_np_array, low_value_np_array, close_value_np_array,
                                        fastk_period=horizon*5, fastd_period=horizon*3, fastd_matype=0)[-1]
            # logger.debug(f'savingStochf value {fastk}, {fastd} for {self.ticker} on {periods} periods')

            new_stochf_storage.periods = periods
            new_stochf_storage.value = f'{fastk}:{fastd}'
            new_stochf_storage.save()

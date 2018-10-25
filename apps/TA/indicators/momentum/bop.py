from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class BopStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class BopSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index is not 'low_price':
            logger.debug(f'index {self.index} is not `low_price` ...ignoring...')
            return

        new_bop_storage = BopStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)


        periods = 2  # doesn't matter, just enough to grab the last one

        open_value_np_array = new_bop_storage.get_denoted_price_array("open_price", periods)
        high_value_np_array = new_bop_storage.get_denoted_price_array("high_price", periods)
        low_value_np_array = new_bop_storage.get_denoted_price_array("low_price", periods)
        close_value_np_array = new_bop_storage.get_denoted_price_array("close_price", periods)

        bop_value = talib.BOP(open_value_np_array, high_value_np_array, low_value_np_array, close_value_np_array)[-1]
        # logger.debug(f'savingBop value {bop_value} for {self.ticker} on {periods} periods')

        new_bop_storage.value = bop_value
        new_bop_storage.save()

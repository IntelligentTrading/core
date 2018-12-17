from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class AroonStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class AroonSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index is not 'low_price':
            logger.debug(f'index {self.index} is not `low_price` ...ignoring...')
            return

        new_aroon_storage = AroonStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 14

            high_value_np_array = new_aroon_storage.get_denoted_price_array("high_price", periods)
            low_value_np_array = new_aroon_storage.get_denoted_price_array("low_price", periods)

            timeperiod = min([len(high_value_np_array), len(low_value_np_array), periods])
            aroondown_value, aroonup_value = talib.AROON(high_value_np_array, low_value_np_array, timeperiod=timeperiod)[-1]
            # logger.debug(f'savingAroon values {aroondown_value}, {aroonup_value} for {self.ticker} on {periods} periods')

            new_aroon_storage.periods = periods
            new_aroon_storage.aroondown = aroondown_value
            new_aroon_storage.aroonup = aroonup_value
            new_aroon_storage.value = ":".join([str(aroondown_value), str(aroonup_value)])
            new_aroon_storage.save()

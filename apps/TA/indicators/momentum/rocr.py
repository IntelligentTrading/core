from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class RocrStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class RocrSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_rocr_storage = RocrStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 10

            close_value_np_array = new_rocr_storage.get_denoted_price_array("close_price", periods)

            timeperiod = min([len(close_value_np_array), periods])
            rocr_value = talib.ROCR(close_value_np_array, timeperiod=timeperiod)[-1]
            # logger.debug(f'savingRocr value {rocr_value} for {self.ticker} on {periods} periods')

            new_rocr_storage.periods = periods
            new_rocr_storage.value = float(rocr_value)
            new_rocr_storage.save()

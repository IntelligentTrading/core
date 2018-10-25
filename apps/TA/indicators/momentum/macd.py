from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class MacdStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class MacdSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_macd_storage = MacdStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 26

            close_value_np_array = new_macd_storage.get_denoted_price_array("close_price", periods)

            macd_value, macdsignal, macdhist = talib.MACD(close_value_np_array, fastperiod=horizon*12, slowperiod=horizon*26, signalperiod=horizon*9)[-1]
            # logger.debug(f'savingMacd value {macd_value} for {self.ticker} on {periods} periods')

            new_macd_storage.periods = periods
            new_macd_storage.value = f'{macd_value}:{macdsignal}:{macdhist}'
            new_macd_storage.save()

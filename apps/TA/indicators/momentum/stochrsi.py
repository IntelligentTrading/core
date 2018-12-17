from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class StochrsiStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class StochrsiSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_stochrsi_storage = StochrsiStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 14

            close_value_np_array = new_stochrsi_storage.get_denoted_price_array("close_price", periods)

            fastk, fastd = talib.STOCHRSI(close_value_np_array, timeperiod=horizon*14,
                                        fastk_period=horizon*5, fastd_period=horizon*3, fastd_matype=0)[-1]
            # logger.debug(f'savingStochrsi value {fastk}, {fastd} for {self.ticker} on {periods} periods')

            new_stochrsi_storage.periods = periods
            new_stochrsi_storage.value = f'{fastk}:{fastd}'
            new_stochrsi_storage.save()

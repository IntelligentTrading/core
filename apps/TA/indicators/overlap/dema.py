from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

DEMA_LIST = [30,]


class DemaStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class DemaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_dema_storage = DemaStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        periods_list = []
        for s in DEMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        for periods in set(periods_list):

            close_value_np_array = new_dema_storage.get_denoted_price_array("close_price", periods)

            dema_value = talib.DEMA(close_value_np_array, timeperiod=periods)[-1]
            # logger.debug(f'savingDema value {dema_value}for {self.ticker} on {periods} periods')

            new_dema_storage.periods = periods
            new_dema_storage.value = float(dema_value)
            new_dema_storage.save()

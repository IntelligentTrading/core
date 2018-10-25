from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class ApoStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class ApoSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_apo_storage = ApoStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 50

            close_value_np_array = self.get_values_array_from_query(
                PriceStorage.query(
                    ticker=self.ticker,
                    exchange=self.exchange,
                    index='close_price',
                    periods_range=periods
                ),
                limit=periods)

            try:
                apo_value = talib.APO(close_value_np_array, fastperiod=12, slowperiod=26, matype=0)[-1]

                # logger.debug(f'savingApo value {apo_value} for {self.ticker} on {periods} periods')
                new_apo_storage.periods = periods
                new_apo_storage.value = int(float(apo_value))
                new_apo_storage.save()

            except Exception as e:
                logger.error(str(e))

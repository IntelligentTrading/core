from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class MidpriceStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class MidpriceSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index is not 'low_price':
            logger.debug(f'index {self.index} is not `high_price` or `low_price` ...ignoring...')
            return

        new_midprice_storage = MidpriceStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 14

            high_value_np_array = self.get_values_array_from_query(
                PriceStorage.query(
                    ticker=self.ticker,
                    exchange=self.exchange,
                    index='high_price',
                    periods_range=periods
                ), 
                limit=periods)

            low_value_np_array = self.get_values_array_from_query(
                PriceStorage.query(
                    ticker=self.ticker,
                    exchange=self.exchange,
                    index='low_price',
                    periods_range=periods
                ), 
                limit=periods)

            timeperiod = min([len(high_value_np_array), len(low_value_np_array), periods])
            midprice_value = talib.MIDPRICE(high_value_np_array, low_value_np_array, timeperiod=timeperiod)[-1]
            logger.debug(f'saving Midprice value {midprice_value}for {self.ticker} on {periods} periods')

            new_midprice_storage.periods = periods
            new_midprice_storage.value = int(float(midprice_value))
            new_midprice_storage.save()

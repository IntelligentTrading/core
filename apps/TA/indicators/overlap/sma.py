from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]


class SmaStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class SmaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    # sorted_set_key = "BTC_USDT:poloniex:SmaStorage:20"

    def handle(self, channel, data, *args, **kwargs):

        """
        now available:
            self.ticker as str
            self.exchange as str
            self.key_suffix as str
            self.timestamp as int
            self.value as str
        """
        # key for PriceStorage like "BLZ_ETH:binance:PriceStorage:close_price"
        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_sma_storage = SmaStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        periods_list = []
        for s in SMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        for periods in set(periods_list):

            # todo: this can be refactored into only one query!
            # todo: after one query for all values, then cut to sizes for horizons and periods
            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                periods_range=periods
            )

            logger.debug(results_dict)

            value_np_array = self.get_values_array_from_query(results_dict, limit=periods)

            sma_value = talib.SMA(value_np_array, timeperiod=periods)[-1]
            # logger.debug(f'savingSMA value {sma_value}for {self.ticker} on {periods} periods')

            new_sma_storage.periods = periods
            new_sma_storage.value = int(float(sma_value))
            new_sma_storage.save()

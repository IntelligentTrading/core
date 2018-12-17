from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS, PERIODS_24HR
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class HtTrendlineStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class HtTrendlineSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_ht_trendline_storage = HtTrendlineStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        results_dict = PriceStorage.query(
            ticker=self.ticker,
            exchange=self.exchange,
            index=self.index,
            periods_range=PERIODS_24HR*200
        )

        value_np_array = new_ht_trendline_storage.get_values_array_from_query(results_dict, limit=PERIODS_24HR*200)

        ht_trendline_value = talib.HT_TRENDLINE(value_np_array)[-1]
        # logger.debug(f'savingHt_trendline value {ht_trendline_value} for {self.ticker}')

        new_ht_trendline_storage.periods = PERIODS_24HR*200
        new_ht_trendline_storage.value = float(ht_trendline_value)
        new_ht_trendline_storage.save()

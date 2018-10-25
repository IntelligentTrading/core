from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

TEMA_LIST = [30,]


class TemaStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class TemaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index != 'close_price':
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_tema_storage = TemaStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        periods_list = []
        for s in TEMA_LIST:
            periods_list.extend([h * s for h in HORIZONS])

        for periods in set(periods_list):

            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                periods_range=periods
            )

            logger.debug(results_dict)

            value_np_array = self.get_values_array_from_query(results_dict, limit=periods)

            tema_value = talib.TEMA(value_np_array, timeperiod=len(value_np_array))[-1]
            # logger.debug(f'savingTema value {tema_value}for {self.ticker} on {periods} periods')

            new_tema_storage.periods = periods
            new_tema_storage.value = int(float(tema_value))
            new_tema_storage.save()

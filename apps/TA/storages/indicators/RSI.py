from settings import LOAD_TALIB
if LOAD_TALIB:
    import talib
import numpy as np

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class RsiStorage(IndicatorStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RsiSubscriber(IndicatorSubscriber):

    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        new_rsi_storage = RsiStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:

            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                periods_range=horizon*14
            )

            value_np_array = self.get_values_array_from_query(results_dict, limit=horizon)

            rsi_value = talib.RSI(value_np_array, timeperiod=len(value_np_array))[-1]
            logger.debug(f'saving RSI value {rsi_value} for {ticker} on {periods} periods')

            new_rsi_storage.periods = horizon
            new_rsi_storage.value = int(float(rsi_value))
            new_rsi_storage.save()

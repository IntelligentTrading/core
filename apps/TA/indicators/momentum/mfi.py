from apps.TA.storages.data.volume import VolumeStorage
from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class MfiStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class MfiSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index is not 'close_price':
            logger.debug(f'index {self.index} is not `close_price` ...ignoring...')
            return

        new_mfi_storage = MfiStorage(ticker=self.ticker,
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

            close_value_np_array = self.get_values_array_from_query(
                PriceStorage.query(
                    ticker=self.ticker,
                    exchange=self.exchange,
                    index='close_price',
                    periods_range=periods
                ),
                limit=periods)

            # ALERT, WE DON'T HAVE VOLUME FOR MANY TICKERS AND IT'S NOT BEING RESAMPLED

            volume_value_np_array = self.get_values_array_from_query(
                VolumeStorage.query(
                    ticker=self.ticker,
                    exchange=self.exchange,
                    index='close_volume',
                    periods_range=periods
                ),
                limit=periods)

            timeperiod = min([len(high_value_np_array), len(low_value_np_array), len(close_value_np_array), periods])
            mfi_value = talib.MFI(high_value_np_array, low_value_np_array, close_value_np_array, volume_value_np_array, timeperiod=timeperiod)[-1]
            logger.debug(f'saving Mfi value {mfi_value} for {self.ticker} on {periods} periods')

            new_mfi_storage.periods = periods
            new_mfi_storage.value = int(float(mfi_value))
            new_mfi_storage.save()

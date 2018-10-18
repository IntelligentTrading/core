from settings import LOAD_TALIB
if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH, OTHER
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class BbandsStorage(IndicatorStorage):

    def produce_signal(self):

        self.width = (self.upperband - self.lowerband) / self.middleband

        bands_of_last_180_periods = BbandsStorage.query(ticker=self.ticker, exchange=self.exchange,
                                     timestamp=self.timestamp, periods=180)

        all_widths = [((bb.upperband - bb.lowerband) / bb.middleband) for bb in bands_of_last_180_periods]
        if self.width <= min(all_widths): # smallest width (squeeze) in the last 180 periods
            # squeeze = True

            if self.price > self.upperband: # price breaks out above the band
                self.trend = BULLISH

            elif self.price < self.lowerband: # price breaks out below the band
                self.trend = BEARISH

            else: # price doesn't break out - but the squeeze thing is cool
                self.trend = OTHER

            self.send_signal(type="BBands", trend=self.trend, width=self.width)



class BbandsSubscriber(IndicatorSubscriber):

    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if self.index is not 'close_price':
            logger.debug(f'index {self.index} is not `close_price` ...ignoring...')
            return

        new_bband_storage = BbandsStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:

            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                periods_range=horizon*5
            )

            value_np_array = self.get_values_array_from_query(results_dict, limit=horizon)

            upperband, middleband, lowerband = talib.BBANDS(
                value_np_array,
                timeperiod=len(value_np_array),
                nbdevup=2, nbdevdn=2, matype=0)

            logger.debug(f'saving Bbands for {self.ticker} on {horizon} periods')

            new_bband_storage.periods = horizon
            new_bband_storage.upperband = upperband
            new_bband_storage.middleband = middleband
            new_bband_storage.lowerband = lowerband
            new_bband_storage.value = ":".join([str(upperband), str(middleband), str(lowerband)])
            new_bband_storage.save()

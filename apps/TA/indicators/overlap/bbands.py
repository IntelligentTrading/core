import math

from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH, OTHER
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class BbandsStorage(IndicatorStorage):

    def get_width(self):
        self.value = self.get_value()
        if self.value:
            [self.upperband_val, self.middleband_val, self.lowerband_val] = [float(val) for val in
                                                                             self.value.split(":")]
            self.width = (self.upperband_val - self.lowerband_val) / self.middleband_val
        else:
            self.width = None
        return self.width

    def produce_signal(self):

        self.value = self.get_value()
        # Bbands value like f"{upperband_val}:{middleband_val}:{lowerband_val}"

        [self.upperband_val, self.middleband_val, self.lowerband_val] = [float(val) for val in self.value.split(":")]
        self.width = (self.upperband_val - self.lowerband_val) / self.middleband_val

        query_result = BbandsStorage.query(
            ticker=self.ticker, exchange=self.exchange, timestamp=self.unix_timestamp, periods=180
        )
        if query_result['values_count'] < 180:
            return  # not enough data

        bbands_values = query_result['values'][-180:]

        upper, middle, lower = 0, 1, 2

        bbands_widths = [(float(v.split(":")[upper]) - float(v.split(":")[lower])) / float(v.split(":")[middle])
                         for v in query_result['values']]

        if self.width <= min(bbands_widths):  # smallest width (squeeze) in the last 180 periods
            # squeeze = True

            self.price = float(PriceStorage.query(ticker=self.ticker, exchange=self.exchange, index="close_price",
                                                  timestamp=self.unix_timestamp)['values'][-1])

            if self.price > self.upperband_val:  # price breaks out above the band
                self.trend = BULLISH

            elif self.price < self.lowerband_val:  # price breaks out below the band
                self.trend = BEARISH

            else:  # price doesn't break out - but the squeeze thing is cool
                self.trend = OTHER

            self.send_signal(type="BBands", trend=self.trend, width=self.width)
            logger.debug("new BBands signal sent")


class BbandsSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    # todo: make handler compiler
    # handle = IndicatorSubscriber.create_handle_method(
    #     index_data = ['close_price'],
    #     storage_class = RocpStorage,
    #     horizon_multiplier=10
    #
    #
    # )

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            # logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_bband_storage = BbandsStorage(ticker=self.ticker,
                                          exchange=self.exchange,
                                          timestamp=self.timestamp)

        for horizon in HORIZONS:

            periods = horizon * 5

            results_dict = PriceStorage.query(
                ticker=self.ticker,
                exchange=self.exchange,
                index=self.index,
                timestamp=self.timestamp,
                periods_range=periods,
            )

            value_np_array = new_bband_storage.get_values_array_from_query(results_dict, limit=periods)

            # todo: add this line to all indicator handlers
            if not len(value_np_array):
                return

            upperband, middleband, lowerband = talib.BBANDS(
                value_np_array,
                timeperiod=periods,
                nbdevup=2, nbdevdn=2, matype=0)

            if math.isnan(upperband[-1] + middleband[-1] + lowerband[-1]):
                return

            new_bband_storage.periods = periods
            new_bband_storage.value = f"{upperband[-1]}:{middleband[-1]}:{lowerband[-1]}"
            new_bband_storage.save()  # will produce signal if necessary
            logger.debug("new BBands value saved")

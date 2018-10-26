from settings import LOAD_TALIB
if LOAD_TALIB:
    import math, talib

from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH, OTHER
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class BbandsStorage(IndicatorStorage):

    class_periods_list = [5]
    requisite_pv_indexes = ["close_price"]

    def get_width(self):
        self.value = self.get_value()
        if self.value:
            [self.upperband_val, self.middleband_val, self.lowerband_val] = [float(val) for val in
                                                                             self.value.split(":")]
            self.width = (self.upperband_val - self.lowerband_val) / self.middleband_val
        else:
            self.width = None
        return self.width


    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        """
        with cls.requisite_pv_indexes set

        :param index_value_arrrays: a dict with keys matching requisite+pv_indexes and values from self.get_denoted_price_array()
        :param periods: number of periods to compute value for
        :return:
        """
        periods = periods or self.periods

        upperband, middleband, lowerband = talib.BBANDS(
            requisite_pv_index_arrrays["close_price"],
            timeperiod=periods,
            nbdevup=2, nbdevdn=2, matype=0
        )

        logger.debug(f"Bbands computed: {upperband[-1]}:{middleband[-1]}:{lowerband[-1]}")

        if math.isnan(sum([upperband[-1], middleband[-1], lowerband[-1]])): return ""

        return f"{upperband[-1]}:{middleband[-1]}:{lowerband[-1]}"


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
    classes_subscribing_to = [PriceStorage]
    storage_class = BbandsStorage

from settings import LOAD_TALIB
if LOAD_TALIB:
    import math, talib

from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH, OTHER
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]


class SmaStorage(IndicatorStorage):
    # example sorted_set_key = "BTC_USDT:poloniex:SmaStorage:20"

    class_periods_list = SMA_LIST
    requisite_pv_indexes = ["close_price"]

    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        """
        with cls.requisite_pv_indexes set

        :param index_value_arrrays: a dict with keys matching requisite+pv_indexes and values from self.get_denoted_price_array()
        :param periods: number of periods to compute value for
        :return:
        """
        periods = periods or self.periods
        sma_value = talib.SMA(requisite_pv_index_arrrays["close_price"], timeperiod=periods)[-1]

        logger.debug(f"SMA computed: {sma_value}")

        if math.isnan(sma_value):
            return ""

        return str(sma_value)


    def produce_signal(self):
        """
        defining the criteria for sending signals

        :return: None
        """
        if "this indicator" == "interesting":
            self.send_signal(trend=BULLISH)


class SmaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [PriceStorage]
    storage_class = SmaStorage

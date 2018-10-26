from settings import LOAD_TALIB
if LOAD_TALIB:
    import math, talib

from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

WMA_LIST = [30, 50, 200,]


class WmaStorage(IndicatorStorage):
    # sorted_set_key = "BTC_USDT:poloniex:WmaStorage:30"

    class_periods_list = WMA_LIST
    requisite_pv_indexes = ["close_price"]

    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        """
        with cls.requisite_pv_indexes set

        :param index_value_arrrays: a dict with keys matching requisite+pv_indexes and values from self.get_denoted_price_array()
        :param periods: number of periods to compute value for
        :return:
        """

        wma_value = talib.WMA(
            requisite_pv_index_arrrays["close_price"],
            timeperiod=periods or self.periods
        )[-1]

        logger.debug(f"WMA computed: {wma_value}")

        if math.isnan(wma_value): return ""

        return str(wma_value)

    def produce_signal(self):
        pass


class WmaSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [PriceStorage]
    storage_class = WmaStorage

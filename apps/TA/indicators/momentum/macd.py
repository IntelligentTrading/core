from settings import LOAD_TALIB
if LOAD_TALIB:
    import math, talib

from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class MacdStorage(IndicatorStorage):

    class_periods_list = [26]
    requisite_pv_indexes = ["close_price"]

    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        """
        with cls.requisite_pv_indexes set

        :param index_value_arrrays: a dict with keys matching requisite+pv_indexes and values from self.get_denoted_price_array()
        :param periods: number of periods to compute value for
        :return:
        """
        periods = periods or self.periods
        fastperiod = periods*12/26
        slowperiod = periods*26/26
        signalperiod = periods*9/26

        macd_value, macdsignal, macdhist = talib.MACD(
            requisite_pv_index_arrrays["close_price"],
            fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod
        )

        logger.debug(f"Macd computed: {macd_value[-1]}:{macdsignal[-1]}:{macdhist[-1]}")

        if math.isnan(sum([macd_value[-1], macdsignal[-1], macdhist[-1]])): return ""

        return f"{macd_value[-1]}:{macdsignal[-1]}:{macdhist[-1]}"

    def produce_signal(self):
        pass

class MacdSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [PriceStorage]
    storage_class = MacdStorage

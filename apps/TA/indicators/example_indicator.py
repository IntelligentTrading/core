from settings import LOAD_TALIB

if LOAD_TALIB:
    import math, talib

from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH, OTHER
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger

EXAMPLE_INDICATOR_PERIODS_LIST = [20, 30, 50]


class ExampleIndicatorStorage(IndicatorStorage):
    # example sorted_set_key = "BTC_USDT:poloniex:ExampleIndicatorStorage:20"

    class_periods_list = EXAMPLE_INDICATOR_PERIODS_LIST
    requisite_pv_indexes = ["close_price", "high_price"]

    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        """
        with cls.requisite_pv_indexes set

        :param index_value_arrrays: a dict with keys matching requisite+pv_indexes and values from self.get_denoted_price_array()
        :param periods: number of periods to compute value for
        :return:
        """
        periods = periods or self.periods  # best practice to keep this line

        example_indicator_value = talib.EXAMPLE(
            requisite_pv_index_arrrays["close_price"],  # 'close_price' is set as a requirement on line 17
            requisite_pv_index_arrrays["high_price"],  # 'close_price' is set as a requirement on line 17
            timeperiod=periods  # usually you are sampling the indicator on the same set of periods as the pv data
        )[-1]  # talib will return an array, so just take the last value

        if math.isnan(example_indicator_value):
            return ""  # best practice to return empty string if no value is available

        return str(example_indicator_value)  # this will save to self.value for each instance
        # for tuple values, format as a string first: eg. f"{example_indicator_value[0]}:{example_indicator_value[1]}"

    def produce_signal(self):
        """
        defining the criteria for sending signals

        :return: None
        """
        if self.value == "interesting":
            self.send_signal(trend=BULLISH)


class ExampleIndicatorSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage  # the handle function below will be called each time a new instance of this class is saved
    ]
    storage_class = ExampleIndicatorStorage

    def handle(self, channel, data, *args, **kwargs):
        # for standard indicators, the default handle method will work
        # it creates instances of the storage class using the compute_value logic above
        super().handle(channel, data, *args, **kwargs)



##### MINIMALIST INDICATOR EXAMPLE #####

class FooStorage(IndicatorStorage):
    class_periods_list = [10, 20]
    requisite_pv_indexes = ["close_price", "close_volume"]

    def compute_value_with_requisite_indexes(self, requisite_pv_index_arrrays: dict, periods: int = 0) -> str:
        foo_value = talib.FOO(requisite_pv_index_arrrays["close_price"], requisite_pv_index_arrrays["close_volume"], timeperiod=periods or self.periods)[-1]
        return str(foo_value) if not math.isnan(foo_value) else ""

    def produce_signal(self):
        self.send_signal(trend=(BULLISH if self.value > 1 else BEARISH))


class FooSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [PriceStorage, ]
    storage_class = ExampleIndicatorStorage

##### MINIMALIST INDICATOR EXAMPLE #####

from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class RocpStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class RocpSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_rocp_storage = RocpStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 10

            close_value_np_array = new_rocp_storage.get_denoted_price_array("close_price", periods)

            timeperiod = min([len(close_value_np_array), periods])
            rocp_value = talib.ROCP(close_value_np_array, timeperiod=timeperiod)[-1]
            # logger.debug(f'savingRocp value {rocp_value} for {self.ticker} on {periods} periods')

            new_rocp_storage.periods = periods
            new_rocp_storage.value = float(rocp_value)
            new_rocp_storage.save()

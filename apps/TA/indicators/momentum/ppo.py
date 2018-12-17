from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class PpoStorage(IndicatorStorage):

    def produce_signal(self):
        pass


class PpoSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_ppo_storage = PpoStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon * 26

            close_value_np_array = new_ppo_storage.get_denoted_price_array("close_price", periods)

            ppo_value = talib.PPO(close_value_np_array, fastperiod=horizon*12, slowperiod=horizon*26, matype=0)[-1]
            # logger.debug(f'savingPpo value {ppo_value} for {self.ticker} on {periods} periods')

            new_ppo_storage.periods = periods
            new_ppo_storage.value = str(ppo_value)
            new_ppo_storage.save()

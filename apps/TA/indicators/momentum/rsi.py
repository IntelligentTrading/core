import numpy as np
from settings import LOAD_TALIB

if LOAD_TALIB:
    import talib

from apps.TA import HORIZONS
from apps.TA.storages.abstract.indicator import IndicatorStorage, BULLISH, BEARISH
from apps.TA.storages.abstract.indicator_subscriber import IndicatorSubscriber
from apps.TA.storages.data.price import PriceStorage
from settings import logger


class RsiStorage(IndicatorStorage):

    def get_rsi_strength(self) -> int:
        rsi = int(self.value)
        if rsi is None or rsi <= 0.0 or rsi >= 100.0:
            return None

        assert (rsi>0.0) & (rsi<100.0), '>>> ERROR: RSI has extreme value of 0 or 100, highly unlikely'

        logger.debug(f"RSI={rsi}")

        rsi_strength = 0
        if rsi >= 80:
            rsi_strength = -3  # Extremely overbought
        elif rsi >= 75:
            rsi_strength = -2  # very overbought
        elif rsi >= 70:
            rsi_strength = -1  # overbought
        elif rsi <= 20:
            rsi_strength = 3  # Extremely oversold
        elif rsi <= 25:
            rsi_strength = 2   # very oversold
        elif rsi <= 30:
            rsi_strength = 1  # oversold
        return rsi_strength

    def produce_signal(self):

        rsi_strength = self.get_rsi_strength()
        if rsi_strength != 0:
            self.send_signal(
                trend=(BULLISH if rsi_strength > 0 else BEARISH),
                strength_value = int(np.abs(rsi_strength)), # should be 1,2,or3
                strength_max = int(3),
            )


class RsiSubscriber(IndicatorSubscriber):
    classes_subscribing_to = [
        PriceStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        self.index = self.key_suffix

        if str(self.index) is not "close_price":
            logger.debug(f'index {self.index} is not close_price ...ignoring...')
            return

        new_rsi_storage = RsiStorage(ticker=self.ticker,
                                     exchange=self.exchange,
                                     timestamp=self.timestamp)

        for horizon in HORIZONS:
            periods = horizon*14

            close_value_np_array = new_rsi_storage.get_denoted_price_array("close_price", periods)

            rsi_value = talib.RSI(close_value_np_array, timeperiod=periods)[-1]
            # logger.debug(f'savingRSI value {rsi_value} for {self.ticker} on {horizon*14} periods')

            new_rsi_storage.periods = horizon
            new_rsi_storage.value = float(rsi_value)
            new_rsi_storage.save()

import logging
from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
import numpy as np

from apps.indicator.models import price_resampl
from settings import time_speed

logger = logging.getLogger(__name__)

class Rsi(AbstractIndicator):
    relative_strength = models.FloatField(null=True)  # relative strength

    @property
    # rsi = 100 - 100 / (1 + rUp / rDown)
    def relative_strength_index(self):  # relative strength index
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))

    def compute_rs(self):
        '''
        Relative Strength calculation.
        The RSI is calculated a a property, we only save RS
        (RSI is a momentum oscillator that measures the speed and change of price movements.)
        :return:
        '''

        # get Series of last 200 time points
        # period= 15,60,360, this ts is already reflects one of those before we call it
        #price_ts = self.get_price_ts()

        time_back = int(15 * self.resample_period)
        resampl_close_price_ts = price_resampl.get_last_close_price_ts(self.resample_period, self.transaction_currency,
                                                                       self.counter_currency, time_back)

        if resampl_close_price_ts is not None:
            # difference btw start and close of the day, remove the first NA
            delta = resampl_close_price_ts.diff()
            delta = delta[1:]

            up, down = delta.copy(), delta.copy()
            up[up < 0] = 0
            down[down > 0] = 0

            # Calculate the 14 period back EWMA for each up/down trends
            # QUESTION: shall this 14 perid depends on period 15,60, 360?
            roll_up = up.ewm(com = 14, min_periods=3).mean()
            roll_down = np.abs(down.ewm(com = 14, min_periods=3).mean())

            rs_ts = roll_up / roll_down

            self.relative_strength = float(rs_ts.tail(1))  # get the last element for the last time point
        else:
            logger.debug('Not enough closing prices for RS calculation')

    @staticmethod
    def run_all(cls, timestamp, source, transaction_currency, counter_currency, resample_period):
        # todo - avoid creation empty record if no rsi was computed

        new_instance = cls.objects.create(
            timestamp=timestamp,
            source=source,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
            resample_period=resample_period,
        )
        new_instance.compute_rs()
        new_instance.save()
        logger.debug("   ...RS calculations done and saved.")



def get_last_rs_value(timestamp, source, transaction_currency, counter_currency, resample_period):
    rs = Rsi.objects.filter(
        timestamp=timestamp,
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        resample_period=resample_period,
    ).order_by('-timestamp').values("relative_strength").last()

    return float(rs['relative_strength'])

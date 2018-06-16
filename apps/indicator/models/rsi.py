from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models import price_resampl
from settings import MODIFY_DB
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Rsi(AbstractIndicator):
    relative_strength = models.FloatField(null=True)  # relative strength

    class Meta:
        indexes = [
            models.Index(fields=['transaction_currency', 'counter_currency', 'source', 'resample_period']),
        ]

    @property
    # rsi = 100 - 100 / (1 + rUp / rDown)
    def rsi(self):  # relative strength index
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))
        else:
            return None

    def get_rsi_bracket_value(self) -> int:
        rsi = self.rsi
        if rsi is None or rsi==0.0 or rsi ==100.0:
            return 0

        assert (rsi>0.0) & (rsi<100.0), '>>> ERROR: RSI has extreme value of 0 or 100, highly unlikely'

        rsi_strength = 0
        if rsi >= 0 and rsi <= 100 :
            logger.debug("   RSI= " + str(rsi))
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


    def compute_rs(self)->float:
        '''
        Relative Strength calculation.
        The RSI is calculated a a property, we only save RS
        (RSI is a momentum oscillator that measures the speed and change of price movements.)
        :return:
        '''

        resampl_price_df = price_resampl.get_n_last_resampl_df(
            20 * self.resample_period,
            self.source, self.transaction_currency, self.counter_currency, self.resample_period
        )

        resampl_close_price_ts = resampl_price_df.close_price
        logger.debug( '  RSI:   current period=' + str(self.resample_period) + ', close prices available for that period=' + str(resampl_close_price_ts.size))

        if (resampl_close_price_ts is not None) and (resampl_close_price_ts.size > 12):
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
            return self.relative_strength
        else:
            logger.debug(':RSI was not calculated:: Not enough closing prices')
            logger.debug('     current period=' + str(self.resample_period) + ', close prices available for that period=' + str(resampl_close_price_ts.size) )
            return None


    @staticmethod
    def compute_all(cls, **kwargs):

        # now we avoid creating DB record if no rsi has been computed
        # the object is only saved if cls.objects.create called
        new_instance = cls(**kwargs)
        rs = new_instance.compute_rs()
        if rs and MODIFY_DB: # modify_db is for debug mode
            new_instance.save()
            logger.info("   ...RS calculation completed and saved.")
        else:
            logger.info("       RSI was not saved (either no value or debug model")




#################
# get last RS value object
'''
def get_last_rs_object(**kwargs):
    rs = Rsi.objects.filter(**kwargs).order_by('-timestamp').last()
    return rs
'''
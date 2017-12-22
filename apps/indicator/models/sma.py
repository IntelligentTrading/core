import logging
from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
import numpy as np

from apps.indicator.models import price
from settings import time_speed

logger = logging.getLogger(__name__)

class Sma(AbstractIndicator):
    sma_period = models.PositiveSmallIntegerField(null=False, default=50)
    sma_close_price = models.BigIntegerField(null=True)

    def compute(self):

        # get resampled data back in time (according to sma period)

        closing_price_ts = raw_prices.resample(rule=self.resample_period).last()

        if closing_price_ts:  # if we have at least one timepoint (to avoid ta-lib SMA error, not nessesary for pandas)
            sma = closing_price_ts.rolling(window=int(self.sma_period/time_speed), center=False, min_periods=4).mean().iloc[-1]

        if not np.isnan(sma):
            self.sma_close_price = int(sma)
        else:
            logger.debug('Not enough closing prices for SMA calculation')
import logging
from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
import numpy as np

from apps.indicator.models import price_resampl
from settings import time_speed

logger = logging.getLogger(__name__)
SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]


class Sma(AbstractIndicator):

    sma_period = models.PositiveSmallIntegerField(null=False, default=50)
    sma_close_price = models.BigIntegerField(null=True)

    def _compute_sma(self):
        time_back = int(np.max(SMA_LIST) * self.resample_period)
        resampl_close_price_ts = price_resampl.get_last_close_price_ts(self.resample_period, self.transaction_currency, self.counter_currency, time_back )

        if not resampl_close_price_ts.empty:
            sma = resampl_close_price_ts.rolling(window=int(self.sma_period/time_speed), center=False).mean().iloc[-1]

        if not np.isnan(sma):
            self.sma_close_price = int(sma)
        else:
            logger.debug('Not enough closing prices for SMA calculation')

    @staticmethod
    def run_all(cls,timestamp,source,transaction_currency,counter_currency,resample_period):
        # todo - avoid creation empty record if no sma was computed
        for sma_period in SMA_LIST:
            new_instance = cls.objects.create(
                timestamp=timestamp,
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency,
                resample_period=resample_period,
                sma_period = sma_period,
            )
            new_instance._compute_sma()
            new_instance.save()
        logger.debug("   ...SMA calculations done and saved.")


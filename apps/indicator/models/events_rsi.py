from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.user.models.user import get_horizon_value_from_string
from apps.indicator.models.rsi import get_last_rs_value
from settings import HORIZONS_TIME2NAMES

import logging
import numpy as np

logger = logging.getLogger(__name__)


class EventsRsi(AbstractIndicator):
    rsi_event_type = models.CharField(max_length=8, null=False, blank=False,default="brackets")
    rsi_bracket = models.PositiveSmallIntegerField(null=False, default=0)

    @staticmethod
    def _get_rsi_bracket_value(rsi):
        assert (rsi>=0.0) & (rsi<=100.0)

        rsi_strength = 0
        if rsi >= 0 and rsi <= 100 :
            logger.debug("   RSI= " + str(rsi))
            if rsi >= 80:
                rsi_strength = 3  # Extremely overbought
            elif rsi >= 75:
                rsi_strength = 2  # very overbought
            elif rsi >= 70:
                rsi_strength = 1  # overbought
            elif rsi <= 20:
                rsi_strength = -3  # Extremely oversold
            elif rsi <= 25:
                rsi_strength = -2   # very oversold
            elif rsi <= 30:
                rsi_strength = -1  # oversold
        return rsi_strength



    @staticmethod
    def run_event_check(cls, timestamp, source, transaction_currency, counter_currency, resample_period):
        rs = get_last_rs_value(timestamp, source, transaction_currency, counter_currency, resample_period)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi_bracket = cls._get_rsi_bracket_value(rsi)
        if rsi_bracket != 0:
            new_instance = cls.objects.create(
                timestamp=timestamp,
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency,
                resample_period=resample_period,
                rsi_event_type = "brackets",
                rsi_bracket = rsi_bracket,
            )
            logger.debug("   ...Events_RSI calculations done and saved.")


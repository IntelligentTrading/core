import logging
from datetime import timedelta, datetime

import numpy as np
import pandas as pd
from django.db import models

from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models import price
from apps.indicator.models.price import Price
from apps.signal.models import Signal
from apps.user.models.user import get_horizon_value_from_string

from settings import HORIZONS_TIME2NAMES  # mapping from bin size to a name short/medium
from settings import PERIODS_LIST
from settings import SHORT, MEDIUM, LONG

from settings import time_speed  # speed of the resampling, 10 for fast debug, 1 for prod

logger = logging.getLogger(__name__)

class PriceResampl(AbstractIndicator):
    # we inherit counter_currency, transaction_currency, resample_period from AbstractIndicator
    open_price = models.BigIntegerField(null=True)
    close_price = models.BigIntegerField(null=True)

    low_price = models.BigIntegerField(null=True)
    high_price = models.BigIntegerField(null=True)
    midpoint_price = models.BigIntegerField(null=True)

    mean_price = models.BigIntegerField(null=True)  # use counter_currency (10^8) for units
    price_variance = models.FloatField(null=True)  # for future signal smoothing


    # compute resampled prices
    def compute(self):
        period_records = Price.objects.filter(timestamp__gte=datetime.now() - timedelta(minutes=self.resample_period))

        transaction_currency_price_list = list(
            period_records.filter(transaction_currency=self.transaction_currency, counter_currency=self.counter_currency).values(
                'timestamp', 'price').order_by('-timestamp'))

        # skip the currency if there is no given price
        if not transaction_currency_price_list:
            logger.debug(' ======= skipping, no price information')
            return

        prices = np.array([rec['price'] for rec in transaction_currency_price_list])

        self.open_price = int(prices[0])
        self.close_price = int(prices[-1])
        self.low_price = int(prices.min())
        self.high_price = int(prices.max())
        self.midpoint_price = None  #todo
        self.mean_price = int(prices.mean())
        self.price_variance = prices.var()


def get_last_close_price_ts(resample_period, transaction_currency, counter_currency, time_back ):
    '''
    Caches from DB the min nessesary amount of records to calculate SMA, EMA etc
    :return: pd.Series of last ~200 time points
    '''
    back_in_time_records = list(PriceResampl.objects.filter(
        resample_period=resample_period,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        # go only back in time for a nessesary period (max of EMA and SMA)
        timestamp__gte = datetime.now() - timedelta(minutes=time_back) # todo add ema_list
    ).values('close_price'))

    if not back_in_time_records:
        return None

    # convert price into a time Series (pandas)
    return pd.Series([rec['close_price'] for rec in back_in_time_records])


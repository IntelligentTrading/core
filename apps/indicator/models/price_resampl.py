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
import logging

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
        # get all prices for one resample period (15/60/360 min)
        period_records = Price.objects.filter(timestamp__gte=datetime.now() - timedelta(minutes=self.resample_period))
        transaction_currency_price_list = list(
            period_records.filter(
                transaction_currency=self.transaction_currency,
                counter_currency=self.counter_currency).values('timestamp', 'price').order_by('-timestamp'))

        # skip the currency if there is no given price
        if transaction_currency_price_list:
            prices = np.array([rec['price'] for rec in transaction_currency_price_list])

            self.open_price = int(prices[0])
            self.close_price = int(prices[-1])
            self.low_price = int(prices.min())
            self.high_price = int(prices.max())
            self.midpoint_price = int((self.high_price + self.low_price) / 2)
            self.mean_price = int(prices.mean())
            self.price_variance = prices.var()
        else:
            logger.debug(' ======= skipping, no price information')



############## get n last records from resampled table as a DataFrame
# NOTE: no kwargs because we dont have timestamp here
def get_n_last_resampl_df(n, source, transaction_currency, counter_currency, resample_period):

    last_prices = list(PriceResampl.objects.filter(
        source=source,
        resample_period=resample_period,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte = datetime.now() - timedelta(minutes=resample_period * n)
    ).values('timestamp', 'high_price', 'close_price', 'midpoint_price').order_by('-timestamp'))

    if last_prices:
        # todo - reverse order or make sure I get values in the same order!
        ts = [rec['timestamp'] for rec in last_prices]
        high_prices = pd.Series(data=[rec['high_price'] for rec in last_prices], index=ts)
        close_prices = pd.Series(data=[rec['close_price'] for rec in last_prices], index=ts)
        midpoint_prices = pd.Series([rec['midpoint_price'] for rec in last_prices], index=ts)

        df = pd.DataFrame()
        df['high_price'] = high_prices
        df['close_price'] = close_prices
        df['midpoint_price'] = midpoint_prices
        return df
    else:
        return None


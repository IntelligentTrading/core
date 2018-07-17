from datetime import timedelta, datetime
import numpy as np
import pandas as pd
from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models.price import Price
from apps.indicator.models.price_history import PriceHistory
import time

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

    # volume field
    open_volume = models.FloatField(null=True)
    close_volume = models.FloatField(null=True)
    low_volume = models.FloatField(null=True)
    high_volume = models.FloatField(null=True)


    class Meta:
        indexes = [
            models.Index(fields=['transaction_currency', 'counter_currency', 'source', 'resample_period', 'timestamp']),
        ]

    # MODEL PROPERTIES
    @property
    def price_change_24h(self):
        current_price_r = self.close_price
        if current_price_r:
            price_r_24h_older = PriceResampl.objects.filter(
                source=self.source,
                resample_period=self.resample_period,
                transaction_currency=self.transaction_currency,
                counter_currency=self.counter_currency,
                timestamp__lte=self.timestamp - timedelta(minutes=1440) # 1440m = 24h
            ).order_by('-timestamp').first()
        try: # FIXME This code smell
            if current_price_r and price_r_24h_older:
                return float(current_price_r - price_r_24h_older.close_price)  / price_r_24h_older.close_price
        except Exception:
            return None


    # compute resampled prices
    def compute(self):
        # set the current time, it might differ from real current time if we calculate prices for old time point

        datetime_now = self.timestamp
        # get all prices for one resample period
        transaction_currency_price_list = list(
            PriceHistory.objects.filter(
                source=self.source,
                transaction_currency=self.transaction_currency,
                counter_currency=self.counter_currency,
                timestamp__lte=datetime_now,
                timestamp__gte=datetime_now - timedelta(minutes=self.resample_period)
            ).values('timestamp', 'close', 'volume').order_by('-timestamp'))

        # skip the currency if there is no given price
        if transaction_currency_price_list:
            prices = np.array([rec['close'] for rec in transaction_currency_price_list])

            self.open_price = int(prices[0])
            self.close_price = int(prices[-1])
            self.low_price = int(prices.min())
            self.high_price = int(prices.max())
            self.midpoint_price = int((self.high_price + self.low_price) / 2)
            self.mean_price = int(prices.mean())
            self.price_variance = prices.var()

            volumes = np.array([rec['volume'] for rec in transaction_currency_price_list])
            self.open_volume = float(volumes[0])
            self.close_volume = float(volumes[-1])
            self.low_volume = float(volumes.min())
            self.high_volume = float(volumes.max())

            return True
        else:
            #logger.debug(' ======= skipping, no price information')
            return False


############## get n last records from resampled table as a DataFrame
# NOTE: no kwargs because we dont have timestamp here
def get_n_last_resampl_df(n, source, transaction_currency, counter_currency, resample_period)->pd.DataFrame:

    last_prices = list(PriceResampl.objects.filter(
        source=source,
        resample_period=resample_period,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte = datetime.now() - timedelta(minutes=resample_period * n)
    ).values('timestamp', 'low_price', 'high_price', 'close_price', 'midpoint_price','mean_price').order_by('-timestamp'))

    df = pd.DataFrame()
    if last_prices:
        # todo - reverse order or make sure I get values in the same order!
        ts = [rec['timestamp'] for rec in last_prices]
        low_prices = pd.Series(data=[rec['low_price'] for rec in last_prices], index=ts)
        high_prices = pd.Series(data=[rec['high_price'] for rec in last_prices], index=ts)
        close_prices = pd.Series(data=[rec['close_price'] for rec in last_prices], index=ts)
        midpoint_prices = pd.Series([rec['midpoint_price'] for rec in last_prices], index=ts)
        mean_prices = pd.Series([rec['mean_price'] for rec in last_prices], index=ts)

        df['low_price'] = low_prices
        df['high_price'] = high_prices
        df['close_price'] = close_prices
        df['midpoint_price'] = midpoint_prices
        df['mean_price'] = mean_prices
        # we need df in a right order (from past to future) to make sma rolling work righ
        df = df.iloc[::-1] # df.sort_index(inplace=True)  might works too

    return df


# get the first element ever resampled
def get_first_resampled_time(source, transaction_currency, counter_currency, resample_period)->float:
    first_time = PriceResampl.objects.filter(
       source=source,
       resample_period=resample_period,
       transaction_currency=transaction_currency,
       counter_currency=counter_currency
   ).values('timestamp').order_by('timestamp').first()

    if first_time :
        return first_time['timestamp'].timestamp()
    else:
        return time.time()


# returns an interpolated resampled price at a given arbitrary time point
def get_resampl_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period)->int:
    '''
    Resampled table contains only agregated prices on 60/240min pime periods, but
    sometimes we need price in between of this points.
    To do that we use this method, which returns an imterpolated prices at arbitraty time point
    based on resample ts data
    Note: to get more presise price use the same method in Price model
    '''

    # look for all prices +/- GRACE_RECORDS around the timepoint
    GRACE_RECORDS = 30
    prices_range = list(PriceResampl.objects.filter(
        source=source,
        resample_period=resample_period,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte = timestamp - timedelta(minutes=resample_period * GRACE_RECORDS),  # 5 period ahead in time
        timestamp__lte=timestamp + timedelta(minutes=resample_period * GRACE_RECORDS),  # 5 period back in time
    ).values('timestamp',  'close_price').order_by('timestamp').distinct())   # we might have bad data with duplications

    #convert to a timeseries
    if prices_range:
        ts = [rec['timestamp'] for rec in prices_range]
        close_prices_ts = pd.Series(data=[rec['close_price'] for rec in prices_range], index=ts)
    else:
        logger.error(' we dont have any resample price in 10 period proximity of the date you provided:  ' + str(timestamp) + ' :backtesting is not possible')
        return None


    # check if we have a timestamp and add it if neccesary
    if timestamp not in close_prices_ts.index:
        # add our missing index, resort and then interpolate
        close_prices_ts = close_prices_ts.append(pd.Series(None, index=[timestamp]))
        close_prices_ts.sort_index(inplace=True)

    # do interpolation and get price
    # we do interpolation because sometimes we have missing data because of bad data collection
    try:
        close_prices_ts = close_prices_ts.interpolate(method='linear', limit=10, limit_direction='both')
        price = int(close_prices_ts[timestamp])
    except Exception as e:
        logger.error(" BAd quality price data, interpolation not possible::  " + str(e))
        return None

    return price

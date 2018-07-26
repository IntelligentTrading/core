#from datetime import timedelta, datetime
import logging
import pandas as pd

import architect

from django.db import models

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



logger = logging.getLogger(__name__)

# IMPORTANT!
#  Run (after any migration in this model):
#  $ export DJANGO_SETTINGS_MODULE=settings; architect partition --module apps.indicator.models.price_history
#  http://architect.readthedocs.io/features/partition/index.html
#
#  You should add indexes manually to existing partitions. Only new partitions (created after changes)
#  will have new indexes.
#  
@architect.install('partition', type='range', subtype='date', constraint='month', column='timestamp')
class PriceHistory(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    transaction_currency = models.CharField(max_length=6, null=False)
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES, null=False)
    open_p = models.BigIntegerField(null=True) # open_p because open is built-in name in Python
    high = models.BigIntegerField(null=True)
    low = models.BigIntegerField(null=True)
    close = models.BigIntegerField(null=True) # please use this as price
    volume = models.FloatField(null=True) # base volume

    timestamp = models.DateTimeField(null=False) # store UTC, timestamp=datetime.datetime.utcfromtimestamp(float(timestamp)/1000.0)


    # INDEX
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'transaction_currency', 'counter_currency', 'source']),
        ]
        unique_together = ('timestamp', 'transaction_currency', 'counter_currency', 'source')


# get n last price records
def get_n_last_prices_ts(n, source, transaction_currency, counter_currency ):
    back_in_time_records = list(PriceHistory.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte=datetime.now() - timedelta(minutes=n)
    ).values('timestamp', 'close', 'volume').order_by('timestamp'))

    if back_in_time_records:
        return pd.Series(
            data= [rec['close'] for rec in back_in_time_records],
            index = [rec['timestamp'] for rec in back_in_time_records]
        )


def get_currency_value_from_string(currency_string):
    currency_dict = {str: i for (i, str) in COUNTER_CURRENCY_CHOICES}
    return currency_dict.get(currency_string, None)


def int_price2float(int_price):
    float_price = float(int_price * 10**-8)


def get_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period)->int:
    prices_range = list(PriceHistory.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte = timestamp - timedelta(minutes=10),  # 10 min ahead in time
        timestamp__lte=timestamp + timedelta(minutes=10),  # 10 min back in time
    ).values('timestamp',  'close').order_by('timestamp'))

    #convert to a timeseries
    if prices_range:
        ts = [rec['timestamp'] for rec in prices_range]
        close_prices_ts = pd.Series(data=[rec['close'] for rec in prices_range], index=ts)
    else:
        logger.error(' we dont have any price in 10 min proximity of the date you provided:  ' + str(timestamp) + ' :backtesting is not possible')
        return None

    # check if we have a price at a given timestamp and if not we interpolate
    if timestamp in close_prices_ts.index:
        price = close_prices_ts[timestamp]
    else:
        # add our missing index, resort and then interpolate
        close_prices_ts = close_prices_ts.append(pd.Series(None, index=[timestamp]))
        close_prices_ts.sort_index(inplace=True)
        close_prices_ts = close_prices_ts.interpolate(method='linear', limit=10, limit_direction='both')
        price = int(close_prices_ts[timestamp])

    return price
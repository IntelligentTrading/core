from datetime import timedelta
from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
#from apps.channel.models.exchange_data import SOURCE_CHOICES
from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, BTC
from datetime import timedelta, datetime
import pandas as pd
import logging

#######################################################################################
# DELETE THIS CLASS AFTER SEPTEMBER 2018 - after make sure PriceHistory works fine!!  #
#######################################################################################

logger = logging.getLogger(__name__)

class Price(models.Model):
    # (BTC, ETH, USDT, XMR) = list(range(4))
    # COUNTER_CURRENCY_CHOICES = (
    #     (BTC, 'BTC'),
    #     (ETH, 'ETH'),
    #     (USDT, 'USDT'),
    #     (XMR, 'XMR'),
    # )
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    transaction_currency = models.CharField(max_length=6, null=False, blank=False)
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES,
                                                null=False, default=BTC)
    price = models.BigIntegerField(null=False)

    timestamp = UnixTimeStampField(null=False)


    # INDEX
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'source', 'transaction_currency', 'counter_currency']),
        ]


    # MODEL PROPERTIES

    @property
    def price_change(self):
        current_price = self.price or self.get_price()
        if current_price:
            fifteen_min_older_price = Price.objects.filter(
                source=self.source,
                transaction_currency=self.transaction_currency,
                counter_currency=self.counter_currency,
                timestamp__lte=self.timestamp - timedelta(minutes=1440)
            ).order_by('-timestamp').first()
        if current_price and fifteen_min_older_price:
            return float(current_price - fifteen_min_older_price.price)  / fifteen_min_older_price.price


# get n last price records

def get_n_last_prices_ts(n, source, transaction_currency, counter_currency ):
    back_in_time_records = list(Price.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte=datetime.now() - timedelta(minutes=n)
    ).values('timestamp', 'price').order_by('timestamp'))

    if back_in_time_records:
        return pd.Series(
            data= [rec['price'] for rec in back_in_time_records],
            index = [rec['timestamp'] for rec in back_in_time_records]
        )


def get_currency_value_from_string(currency_string):
    currency_dict = {str: i for (i, str) in COUNTER_CURRENCY_CHOICES}
    return currency_dict.get(currency_string, None)


def int_price2float(int_price):
    float_price = float(int_price * 10**-8)


def get_price_at_timepoint(timestamp, source, transaction_currency, counter_currency, resample_period)->int:

    prices_range = list(Price.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte = timestamp - timedelta(minutes=10),  # 10 min ahead in time
        timestamp__lte=timestamp + timedelta(minutes=10),  # 10 min back in time
    ).values('timestamp',  'price').order_by('timestamp'))

    #convert to a timeseries
    if prices_range:
        ts = [rec['timestamp'] for rec in prices_range]
        close_prices_ts = pd.Series(data=[rec['price'] for rec in prices_range], index=ts)
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
#######################################################################################
# DELETE THIS CLASS AFTER SEPTEMBER 2018 - after make sure PriceHistory works fine!!  #
#######################################################################################
# volume now is in price_history table

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

#from apps.channel.models.exchange_data import SOURCE_CHOICES
#from apps.indicator.models.price import Price

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, BTC

from datetime import timedelta, datetime
import pandas as pd

class Volume(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    transaction_currency = models.CharField(max_length=6, null=False, blank=False)
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES, null=False, default=BTC)

    volume = models.FloatField(null=False)
    timestamp = UnixTimeStampField(null=False)

    # INDEX
    class Meta:
        indexes = [
            models.Index(fields=['transaction_currency', 'counter_currency', 'source', 'timestamp']),
        ]

    # MODEL PROPERTIES

    # MODEL FUNCTIONS

#TODO: @Karla, we need to use Volume resampled here.. and switch to PriceHistory
def get_n_last_volumes_ts(n, source, transaction_currency, counter_currency):
    back_in_time_records = list(Volume.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        timestamp__gte=datetime.now() - timedelta(minutes=n)
    ).values('timestamp', 'volume').order_by('timestamp'))

    if back_in_time_records:
        return pd.Series(
            data = [rec['volume'] for rec in back_in_time_records],
            index=[rec['timestamp'] for rec in back_in_time_records]
        )
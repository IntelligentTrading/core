#from datetime import timedelta, datetime
import logging
import pandas as pd

import architect

from django.db import models

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



logger = logging.getLogger(__name__)

# Run: export DJANGO_SETTINGS_MODULE=settings; architect partition --module apps.indicator.models.price_history #after any migration in this model
@architect.install('partition', type='range', subtype='date', constraint='month', column='timestamp')
class PriceHistory(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    transaction_currency = models.CharField(max_length=6, null=False)
    counter_currency = models.SmallIntegerField(choices=COUNTER_CURRENCY_CHOICES, null=False)
    open_p = models.BigIntegerField(null=True) # open_p because open is built-in name in Python
    high = models.BigIntegerField(null=True)
    low = models.BigIntegerField(null=True)
    close = models.BigIntegerField(null=True) # please use this as price

    timestamp = models.DateTimeField(null=False) # store UTC, timestamp=datetime.datetime.utcfromtimestamp(float(timestamp)/1000.0)


    # INDEX FIXME enable it later after importing all data (it's faster w/o index)
    # class Meta:
    #     indexes = [
    #         models.Index(fields=['timestamp', 'source', 'transaction_currency', 'counter_currency']),
    #     ]

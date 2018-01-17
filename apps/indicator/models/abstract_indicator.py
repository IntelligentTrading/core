from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models.price import Price


class AbstractIndicator(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    counter_currency = models.SmallIntegerField(choices=Price.COUNTER_CURRENCY_CHOICES, null=False, default=Price.BTC)
    transaction_currency = models.CharField(max_length=6, null=False, blank=False)
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

    class Meta:
        abstract = True

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES


class Price(models.Model):
    class Meta:
        unique_together = (('coin', 'timestamp'),)

    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)

    satoshis = models.BigIntegerField(null=False) # satoshis
    wei = models.BigIntegerField(null=True)  # wei
    usdt = models.FloatField(null=True) # USD value

    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

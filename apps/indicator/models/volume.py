from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES

class Volume(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)

    btc_volume = models.FloatField(null=False)
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

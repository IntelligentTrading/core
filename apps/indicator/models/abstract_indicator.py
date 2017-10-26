from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES


class AbstractIndicator(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

    class Meta:
        abstract = True
from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from datetime import timedelta
from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models.abstract_indicator import AbstractIndicator


class PriceResampled(AbstractIndicator):
    # source inherited from AbstractIndicator
    # coin inherited from AbstractIndicator
    # timestamp inherited from AbstractIndicator

    period = models.PositiveSmallIntegerField(null=False, default=15)  # minutes (eg. 15)

    mean_price_satoshis = models.IntegerField(null=True) # satoshis
    min_price_satoshis = models.IntegerField(null=True) # satoshis
    max_price_satoshis = models.IntegerField(null=True) # satoshis

    SMA50_satoshis = models.IntegerField(null=True) # satoshis
    SMA200_satoshis = models.IntegerField(null=True) # satoshis

    # EMA50
    # EMA200


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

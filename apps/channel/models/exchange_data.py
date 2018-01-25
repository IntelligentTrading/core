from django.db import models
from django.contrib.postgres.fields import JSONField
from unixtimestampfield.fields import UnixTimeStampField


(POLONIEX, BITTREX, BINANCE) = list(range(3))
SOURCE_CHOICES = (
    (POLONIEX, 'poloniex'),
    (BITTREX, 'bittrex'),
    (BINANCE, 'binance'),
)


class ExchangeData(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    data = models.TextField(default="")
    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS

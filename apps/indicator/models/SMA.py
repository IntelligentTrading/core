from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from datetime import timedelta
from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models.abstract_indicator import AbstractIndicator


class SMA(AbstractIndicator):
    # source inherited from AbstractIndicator
    # coin inherited from AbstractIndicator
    # timestamp inherited from AbstractIndicator

    period_size = models.PositiveSmallIntegerField(null=False)
    period_count = models.PositiveSmallIntegerField(null=False)
    value = models.IntegerField(null=False) # satoshis


    # MODEL PROPERTIES

    # MODEL FUNCTIONS


def compile_sma_values_from_price(price):

    for period_size in [5, 30, 120]:

        previous_sma = SMA.objects.filter(coin=price.coin, period_size=price.period_size).order_by('-timestamp').first()

        if previous_sma.timestamp + timedelta(minutes=period_size) <= price.timestamp:
            # now we need to compile and store new MA values for each period count

            for period_count in [5, 50, 200]:

                value = None

                # calc value

                new_SMA = SMA.objects.create(
                    source = price.source,
                    coin=price.coin,
                    timestamp=previous_sma.timestamp + timedelta(minutes=period_size),
                    period_size=period_size,
                    period_count=period_count,
                    value=value
                )

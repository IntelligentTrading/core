from datetime import timedelta

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES


class Price(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)

    satoshis = models.BigIntegerField(null=False) # satoshis
    wei = models.BigIntegerField(null=True)  # wei
    usdt = models.FloatField(null=True) # USD value

    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    # MODEL FUNCTIONS



    @property
    def price_change(self):
        past_price = Price.objects.filter(
            source=self.source,
            coin=self.coin,
            timestamp__lte=self.timestamp - timedelta(minutes=15)
        ).order_by("-timestamp")[0]
        return float(self.price - past_price.satoshis) / past_price.satoshis

from datetime import timedelta

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField

from apps.channel.models.exchange_data import SOURCE_CHOICES


(BTC, ETH, USDT, XMR) = list(range(3))
COIN_CHOICES = (
    (BTC, 'BTC'),
    (ETH, 'ETH'),
    (USDT, 'USDT'),
    (XMR, 'XMR'),
)


class Price(models.Model):
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    base_coin = models.SmallIntegerField(choices=COIN_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)

    price = models.BigIntegerField(null=False) # price_satoshis

    timestamp = UnixTimeStampField(null=False)


    # MODEL PROPERTIES

    @property
    def price_satoshis_change(self):

        past_price = Price.objects.filter(
            source=self.source,
            coin=self.coin,
            timestamp__lte=self.timestamp - timedelta(minutes=15)
        ).order_by("-timestamp").first()

        if past_price:
            return float(self.price_satoshis - past_price.price_satoshis) / past_price.price_satoshis

    @property
    def price_usdt_change(self):
        current_price_usdt = self.price_usdt or self.get_price_usdt()
        if current_price_usdt:
            fifteen_min_older_price_usdt = Price.objects.filter(
                source=self.source,
                coin=self.coin,
                timestamp__lte=self.timestamp - timedelta(minutes=15),
                price_usdt__isnull=False
            ).order_by('-timestamp').first()
        if current_price_usdt and fifteen_min_older_price_usdt:
            return current_price_usdt - fifteen_min_older_price_usdt.price_usdt


    # MODEL FUNCTIONS
    def get_price_usdt(self):
        btc_price = Price.objects.filter(
            source=self.source,
            coin=self.coin,
            timestamp__gte=self.timestamp - timedelta(minutes=1),
            timestamp__lte=self.timestamp + timedelta(minutes=1),
            price_usdt__isnull=False
        ).order_by('-timestamp').first()
        if btc_price:
            self.price_usdt = btc_price.price_usdt
        return self.price_usdt

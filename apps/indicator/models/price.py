from datetime import timedelta
from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from apps.channel.models.exchange_data import SOURCE_CHOICES


class Price(models.Model):
    (BTC, ETH, USDT, XMR) = list(range(4))
    BASE_COIN_CHOICES = (
        (BTC, 'BTC'),
        (ETH, 'ETH'),
        (USDT, 'USDT'),
        (XMR, 'XMR'),
    )
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    coin = models.CharField(max_length=6, null=False, blank=False)
    base_coin = models.SmallIntegerField(choices=BASE_COIN_CHOICES,
                                         null=False, default=BTC)
    price = models.BigIntegerField(null=False)

    timestamp = UnixTimeStampField(null=False)

    # MODEL PROPERTIES

    @property
    def price_change(self):
        current_price = self.price or self.get_price()
        if current_price:
            fifteen_min_older_price = Price.objects.filter(
                source=self.source,
                coin=self.coin,
                base_coin=self.base_coin,
                timestamp__lte=self.timestamp - timedelta(minutes=15)
            ).order_by('-timestamp').first()
        if current_price and fifteen_min_older_price:
            return current_price - fifteen_min_older_price.price


    # MODEL FUNCTIONS



def get_coin_value_from_string(coin_string):
    coin_dict = {str: i for (i, str) in Price.BASE_COIN_CHOICES}
    return coin_dict.get(coin_string, None)

def int_price2float(int_price):
    float_price = float(int_price * 10**-8)
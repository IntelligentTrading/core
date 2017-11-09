import json
import logging

import boto
from boto.sqs.message import Message
from datetime import datetime

from django.db.models.signals import post_save

from apps.common.behaviors import Timestampable
from apps.indicator.models import Price
from settings import QUEUE_NAME, AWS_OPTIONS, TEST_QUEUE_NAME
from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from apps.channel.models.exchange_data import SOURCE_CHOICES, POLONIEX
from apps.user.models.user import RISK_CHOICES, HORIZON_CHOICES

logger = logging.getLogger(__name__)


(TELEGRAM, WEB) = list(range(2))
UI_CHOICES = (
    (TELEGRAM, 'telegram bot'),
    (WEB, 'web app'),
)


class Signal(Timestampable, models.Model):

    UI = models.SmallIntegerField(choices=UI_CHOICES, null=False, default=TELEGRAM)
    subscribers_only = models.BooleanField(default=True)
    text = models.TextField(default="")

    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False, default=POLONIEX)
    coin = models.CharField(max_length=6, null=False, blank=False)

    signal = models.CharField(max_length=15, null=True)
    trend = models.CharField(max_length=15, null=True)

    risk = models.SmallIntegerField(choices=RISK_CHOICES, null=True)
    horizon = models.SmallIntegerField(choices=HORIZON_CHOICES, null=True)
    strength_value = models.IntegerField(null=True)
    strength_max = models.IntegerField(null=True)

    price_satoshis = models.BigIntegerField(null=False)  # Price in satoshis
    price_satoshis_change = models.FloatField(null=True)
    price_usdt = models.FloatField(null=True)  # USD value
    price_usdt_change = models.FloatField(null=True)

    volume_btc = models.FloatField(null=True)  # BTC volume
    volume_btc_change = models.FloatField(null=True)
    volume_usdt = models.FloatField(null=True)  # USD value
    volume_usdt_change = models.FloatField(null=True)

    sent_at = UnixTimeStampField(null=False)

    # MODEL PROPERTIES


    # MODEL FUNCTIONS

    def get_price_satoshis(self):
        if self.price_satoshis and self.price_satoshis_change:
            return self.price_satoshis

        price_object = Price.objects.filter(coin=self.coin,
                                            source=self.source,
                                            timestamp__lte=self.timestamp
                                            ).order_by('-timestamp')[0]
        self.price_satoshis = price_object.price_satoshis
        self.price_satoshis_change = price_object.price_satoshis_change
        return self.price_satoshis


    def _send(self):

        # populate all required values

        try:
            if not self.price_satoshis or not self.price_satoshis_change:
                self.price_satoshis = self.get_price_satoshis()

            if not self.volume or not self.volume_change:
                pass #todo write and call volume getter function

        except Exception as e:
            logging.debug("Problem finding price, volume: " + str(e))

        alert_data = json.dumps(self.__dict__)


        # todo: call send in a post_save signal?? is there any reason to delay or schedule a signal?

        message = Message()
        message.set_body(alert_data)

        sqs_connection = boto.sqs.connect_to_region("us-east-1",
                            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'])
        production_queue = sqs_connection.get_queue(QUEUE_NAME)
        production_queue.write(message)
        if TEST_QUEUE_NAME:
            test_queue = sqs_connection.get_queue(TEST_QUEUE_NAME)
            test_queue.write(message)

        self.sent_at = datetime.now()

    def print(self):
        logger.info("EMITTED SIGNAL: " + str(self.__dict__))


from django.db.models.signals import post_save
from django.dispatch import receiver

# method for updating
@receiver(post_save, sender=Signal, dispatch_uid="update_stock_count")
def send_signal(sender, instance, **kwargs):
    if not instance.sent_at:
        try:
            instance._send()
            assert instance.sent_at
            instance.save()
        except Exception as e:
            logging.debug(str(e))

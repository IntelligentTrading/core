import json
import logging

import boto
from boto.sqs.message import Message
from datetime import datetime

from apps.common.behaviors import Timestampable
from apps.indicator.models import Price
from settings import QUEUE_NAME, AWS_OPTIONS
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

    def send(self):

        # populate all required values

        try:
            if not self.price_change:
                price_object = Price.objects.filter(coin=self.coin,
                                                    source=self.source,
                                                    satoshis=self.price_satoshis
                                                    ).order_by('-timestamp')[0]
                self.price_satoshis_change = price_object.price_satoshis_change

            if not self.volume or self.volume_change:
                pass

        except Exception as e:
            logging.debug("Problem finding price, volume: " + str(e))

        alert_data = json.dumps(self.__dict__)


        # todo: call send in a post_save signal?? is there any reason to delay or schedule a signal?

        # todo: prevent sending again

        sqs_connection = boto.sqs.connect_to_region("us-east-1",
                            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'])
        queue = sqs_connection.get_queue(QUEUE_NAME)
        message = Message()
        message.set_body(alert_data)
        queue.write(message)

        self.sent_at = datetime.now()


    def print(self):
        logger.info("EMITTED SIGNAL: coin=" + str(self.coin) +
                    " signal=" + str(self.signal) +
                    " trend=" + str(self.trend) +
                    " horizon=" + str(self.horizon) +
                    " strength_value=" + str(self.strength_value))



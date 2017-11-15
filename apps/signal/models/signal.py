import copy
import json
import logging

import boto
from boto.sqs.message import Message
from datetime import datetime

from django.db.models.signals import post_save, pre_save

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

    timestamp = UnixTimeStampField(null=False)
    sent_at = UnixTimeStampField(use_numeric=True)

    # MODEL PROPERTIES


    # MODEL FUNCTIONS

    def get_price_satoshis(self):
        if self.price_satoshis and self.price_satoshis_change:
            return self.price_satoshis

        price_object = Price.objects.filter(coin=self.coin,
                                            source=self.source,
                                            timestamp__lte=self.timestamp
                                            ).order_by('-timestamp').first()
        if price_object:
            self.price_satoshis = price_object.price_satoshis
            self.price_satoshis_change = price_object.price_satoshis_change
            self.price_usdt = price_object.price_usdt
            self.price_usdt_change = price_object.price_usdt_change
        return self.price_satoshis


    def as_dict(self):
        data_dict = copy.deepcopy(self.__dict__)
        if "_state" in data_dict:
            del data_dict["_state"]
        data_dict.update({
            "UI": self.get_UI_display(),
            "source": self.get_source_display(),
            "risk": self.get_risk_display(),
            "horizon": self.get_horizon_display(),
            "created_at": str(self.created_at),
            "modified_at": str(self.modified_at),
            "timestamp": str(self.timestamp),
            "sent_at": str(self.sent_at),
        })
        return data_dict

    def _send(self):
        # populate all required values

        try:
            if not all([self.price_satoshis, self.price_satoshis_change,
                        self.price_usdt, self.price_usdt_change]):
                self.price_satoshis = self.get_price_satoshis()

            if not all([self.volume_btc, self.volume_btc_change,
                        self.volume_usdt, self.volume_usdt_change]):
                pass #todo write and call volume getter function

        except Exception as e:
            logging.debug("Problem finding price, volume: " + str(e))


        # todo: call send in a post_save signal?? is there any reason to delay or schedule a signal?

        message = Message()
        message.set_body(json.dumps(self.as_dict()))

        sqs_connection = boto.sqs.connect_to_region("us-east-1",
                            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'])
        production_queue = sqs_connection.get_queue(QUEUE_NAME)
        production_queue.write(message)
        if TEST_QUEUE_NAME:
            test_queue = sqs_connection.get_queue(TEST_QUEUE_NAME)
            test_queue.write(message)

        logger.debug("EMITTED SIGNAL: " + str(self.as_dict()))
        self.sent_at = datetime.now()
        return


    def print(self):
        logger.info("EMITTED SIGNAL: " + str(self.as_dict()))


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(pre_save, sender=Signal, dispatch_uid="check_has_price_satoshis")
def check_has_price_satoshis(sender, instance, **kwargs):
    price_satoshis = instance.get_price_satoshis()
    try:
        assert price_satoshis #see now we have it :)
    except Exception as e:
        logging.debug(str(e))


@receiver(post_save, sender=Signal, dispatch_uid="send_signal")
def send_signal(sender, instance, **kwargs):
    if not instance.sent_at:
        try:
            instance._send()
            assert instance.sent_at
            instance.save()
        except Exception as e:
            logging.error(str(e))

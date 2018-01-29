import copy
import json
import logging

import boto
from boto.sqs.message import Message
from datetime import datetime

from django.db.models.signals import post_save, pre_save

from apps.common.behaviors import Timestampable
from apps.indicator.models import Price
from settings import QUEUE_NAME, AWS_OPTIONS, BETA_QUEUE_NAME, TEST_QUEUE_NAME, PERIODS_LIST
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

    timestamp = UnixTimeStampField(null=False)
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False, default=POLONIEX)
    transaction_currency = models.CharField(max_length=6, null=False, blank=False)
    counter_currency = models.SmallIntegerField(choices=Price.COUNTER_CURRENCY_CHOICES, null=False, default=Price.BTC)
    resample_period = models.PositiveSmallIntegerField(null=False, default=PERIODS_LIST[0])

    signal = models.CharField(max_length=15, null=True)
    trend = models.CharField(max_length=15, null=True)

    risk = models.SmallIntegerField(choices=RISK_CHOICES, null=True)
    horizon = models.SmallIntegerField(choices=HORIZON_CHOICES, null=True)
    strength_value = models.IntegerField(null=True)
    strength_max = models.IntegerField(null=True)

    price = models.BigIntegerField(null=False)
    price_change = models.FloatField(null=True)  # in percents, thatis why Float

    rsi_value = models.FloatField(null=True)

    volume_btc = models.FloatField(null=True)  # BTC volume
    volume_btc_change = models.FloatField(null=True)
    volume_usdt = models.FloatField(null=True)  # USD value
    volume_usdt_change = models.FloatField(null=True)

    sent_at = UnixTimeStampField(use_numeric=True)

    # MODEL PROPERTIES


    # MODEL FUNCTIONS

    def get_price(self):
        if self.price and self.price_change:
            return self.price

        price_object = Price.objects.filter(transaction_currency=self.transaction_currency,
                                            source=self.source,
                                            counter_currency = self.counter_currency,
                                            timestamp__lte=self.timestamp
                                            ).order_by('-timestamp').first()
        if price_object:
            self.price = price_object.price
            self.price_change = price_object.price_change
        return self.price


    def as_dict(self):
        data_dict = copy.deepcopy(self.__dict__)
        if "_state" in data_dict:
            del data_dict["_state"]
        for key, value in data_dict.items():
            data_dict[key] = str(value) # cast all as strings
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
            if not all([self.price, self.price_change]):
                self.price = self.get_price()

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

        if QUEUE_NAME:
            logging.debug("emitted to QUEUE_NAME queue :" + QUEUE_NAME)
            production_queue = sqs_connection.get_queue(QUEUE_NAME)
            production_queue.write(message)

        if BETA_QUEUE_NAME:
            logging.debug("emitted to BETA_QUEUE_NAME queue :" + BETA_QUEUE_NAME)
            test_queue = sqs_connection.get_queue(BETA_QUEUE_NAME)
            test_queue.write(message)

        if TEST_QUEUE_NAME:
            logging.debug("emitted to TEST_QUEUE_NAME queue :" + TEST_QUEUE_NAME)
            test_queue = sqs_connection.get_queue(TEST_QUEUE_NAME)
            test_queue.write(message)

        logger.info("EMITTED SIGNAL: " + str(self.as_dict()))
        self.sent_at = datetime.now()  # to prevent emitting the same signal twice
        return

    def print(self):
        logger.info("PRINTING SIGNAL DATA: " + str(self.as_dict()))

    def _same_as_previous(self):
        # todo: get one day back in time and check if all fileds are the same - no reason to send it twice
        return False


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(pre_save, sender=Signal, dispatch_uid="check_has_price")
def check_has_price(sender, instance, **kwargs):
    price = instance.get_price()
    try:
        assert price #see now we have it :)
    except Exception as e:
        logging.debug(str(e))


@receiver(post_save, sender=Signal, dispatch_uid="send_signal")
def send_signal(sender, instance, **kwargs):
    logging.debug("signal saved, checking if signal has been sent yet")
    if not instance.sent_at:   # to prevent emitting the same signal twice
        try:
            logging.debug("signal not sent yet, sending now...")
            instance._send()
            assert instance.sent_at
            instance.save()
            logging.debug("signal sent and timstamp saved")
        except Exception as e:
            logging.error(str(e))

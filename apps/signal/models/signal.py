import json
import logging

import boto
from boto.sqs.message import Message

from apps.common.behaviors import Timestampable
from apps.indicator.models import Price
from settings import QUEUE_NAME, AWS_OPTIONS
from django.db import models


logger = logging.getLogger(__name__)


class Signal(Timestampable, models.Model):
    def __init__(self, *args, **kwargs): #todo: lookup what is init best practice!!
        self.UI = "Telegram"
        self.subscribers_only = True
        self.text = kwargs.get('text', None)

        self.source = kwargs.get('coin', "Poloniex")
        self.coin = kwargs.get('coin', None)
        self.market = kwargs.get('market', None)
        self.signal = kwargs.get('signal', None)
        self.trend = kwargs.get('trend', None)

        self.risk = kwargs.get('risk', None)
        self.horizon = kwargs.get('horizon', None)
        self.strength_value = kwargs.get('strength_value', None)
        self.strength_max = kwargs.get('strength_max', None)

        self.price_satoshis = kwargs.get('price_satoshis', None)
        self.price_satoshis_change = kwargs.get('price_satoshis_change', None)
        self.price_usdt = kwargs.get('price_usdt', None)
        self.price_usdt_change = kwargs.get('price_usdt_change', None)

        self.volume_btc = kwargs.get('volume', None)
        self.volume_btc_change = kwargs.get('volume_change', None)
        self.volume_usdt = kwargs.get('volume', None)
        self.volume_usdt_change = kwargs.get('volume_change', None)

        self.print()


    def send(self):
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

        sqs_connection = boto.sqs.connect_to_region("us-east-1",
                            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'])
        queue = sqs_connection.get_queue(QUEUE_NAME)
        message = Message()
        message.set_body(alert_data)
        queue.write(message)


    def print(self):
        logger.info("EMITTED SIGNAL: coin=" + str(self.coin) +
                    " signal=" + str(self.signal) +
                    " trend=" + str(self.trend) +
                    " horizon=" + str(self.horizon) +
                    " strength_value=" + str(self.strength_value))

        # coin=BTC
        # market=Poloniex
        # signal=SMA
        # trend=BEARISH
        # risk=medium
        # horizon=medium
        # strength_value=1
        # strength_max=3
        # price=4814
        # price_satoshis_change=0.0028

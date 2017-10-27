import json

import boto
from boto.sqs.message import Message

from settings import QUEUE_NAME, AWS_OPTIONS


class TelegramAlert(object):
    def __init__(self, *args, **kwargs):
        self.UI = "Telegram"
        self.subscribers_only = True
        self.text = kwargs.get('text', None)

        self.coin = kwargs.get('coin', None)
        self.market = kwargs.get('market', None)
        self.signal = kwargs.get('signal', None)
        self.trend = kwargs.get('trend', None)

        self.risk = kwargs.get('risk', None)
        self.horizon = kwargs.get('horizon', None)
        self.strength_value = kwargs.get('strength_value', None)
        self.strength_max = kwargs.get('strength_max', None)

        self.price = kwargs.get('price', None)
        self.price_change = kwargs.get('price_change', None)
        self.volume = kwargs.get('volume', None)
        self.volume_change = kwargs.get('volume_change', None)

    def get_price_info(self):
        if self.coin:
            prices = Price.objects.filter(coin=self.coin).order_by("-timestamp")[0:15]
            self.price = prices[0].satoshis
            self.price_change = (prices[0].satoshis - prices[14].satoshis) / prices[0].satoshis

    def send(self):
        if not (self.price and self.price_change):
            self.get_price_info()

        alert_data = json.dumps(self.__dict__)

        sqs_connection = boto.sqs.connect_to_region("us-east-1",
                            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'])
        queue = sqs_connection.get_queue(QUEUE_NAME)
        message = Message()
        message.set_body(alert_data)
        queue.write(message)


        # coin=BTC
        # market=Poloniex
        # signal=SMA
        # trend=BEARISH
        # risk=medium
        # horizon=medium
        # strength_value=1
        # strength_max=3
        # price=4814
        # price_change=0.0028

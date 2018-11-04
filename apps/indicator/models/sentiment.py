from datetime import timedelta
from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
#from apps.channel.models.exchange_data import SOURCE_CHOICES
from settings import SENTIMENT_SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, SENTIMENT_MODEL_CHOICES
from datetime import timedelta, datetime
import pandas as pd
import logging
from settings import time_speed, MODIFY_DB


logger = logging.getLogger(__name__)

class Sentiment(models.Model):
    # (BTC, ETH, USDT, XMR) = list(range(4))
    # COUNTER_CURRENCY_CHOICES = (
    #     (BTC, 'BTC'),
    #     (ETH, 'ETH'),
    #     (USDT, 'USDT'),
    #     (XMR, 'XMR'),
    # )
    sentiment_source = models.SmallIntegerField(choices=SENTIMENT_SOURCE_CHOICES, null=False)
    topic = models.CharField(max_length=6, null=False, blank=False)
    model = models.SmallIntegerField(choices=SENTIMENT_MODEL_CHOICES, null=False)
    positive = models.FloatField(null=False)
    negative = models.FloatField(null=False)
    neutral = models.FloatField(null=False)
    compound = models.FloatField(null=False)
    timestamp = UnixTimeStampField(null=False)


    # INDEX
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'model', 'sentiment_source', 'topic']),
        ]

    def _compute(self, timestamp):
        self.sentiment_source = 0
        self.topic = 'BTC'
        self.model = 0
        self.positive = 0.23
        self.neutral = 0.55
        self.negative = 0.22
        self.compound = -0.56
        self.timestamp = timestamp

    @staticmethod
    def compute_all(timestamp):
        try:
            sentiment_instance = Sentiment()
            sentiment_instance._compute(timestamp)
            if MODIFY_DB:
                sentiment_instance.save()
        except Exception as e:
            logger.error(" Compute Exception: " + str(e))
        logger.info("   ...All sentiment calculations have been done and saved.")

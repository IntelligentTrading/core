import logging
from django.db import models
from django.db.models.signals import post_save, pre_save

from apps.common.behaviors import Timestampable


logger = logging.getLogger(__name__)


class Portfolio(Timestampable, models.Model):

    binance_API_key = models.CharField(max_length=50)
    binance_API_secret = models.CharField(max_length=50)

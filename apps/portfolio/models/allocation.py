import logging
from django.db import models
from django.db.models.signals import post_save, pre_save

from apps.common.behaviors import Timestampable


logger = logging.getLogger(__name__)


class Allocation(models.Model):

    portfolio = models.ForeignKey("portfolio.Portfolio")
    currency = models.CharField(max_length=5, null=False)
    portion = models.FloatField(default=0.0)

import logging
from django.db import models
from apps.common.behaviors import Timestampable

logger = logging.getLogger(__name__)


class TelegramBot(Timestampable, models.Model):

    token = models.CharField(max_length=100, default="")
    title = models.CharField(max_length=100, default="")
    username = models.CharField(max_length=100, default="")

    # MODEL PROPERTIES

    # MODEL FUNCTIONS

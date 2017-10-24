import uuid
import logging
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.behaviors import Timestampable


class User(AbstractUser, Timestampable):
    USERNAME_FIELD = 'telegram_chat_id'
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS
    REQUIRED_FIELDS.remove('email')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    telegram_chat_id = models.CharField(max_length=128, null=False)
    is_subscribed = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)

    (LOW_RISK, MEDIUM_RISK, HIGH_RISK) = list(range(3))
    RISK_CHOICES = (
        (LOW_RISK, 'low'),
        (MEDIUM_RISK, 'medium'),
        (HIGH_RISK, 'high'),
    )
    risk = models.SmallIntegerField(choices=RISK_CHOICES, default=LOW_RISK)

    (SHORT_HORIZON, MEDIUM_HORIZON, LONG_HORIZON) = list(range(3))
    HORIZON_CHOICES = (
        (SHORT_HORIZON, 'short'),
        (MEDIUM_HORIZON, 'medium'),
        (LONG_HORIZON, 'long'),
    )
    horizon = models.SmallIntegerField(choices=HORIZON_CHOICES, default=MEDIUM_HORIZON)


    # MODEL PROPERTIES


    # MODEL FUNCTIONS


User._meta.get_field('username')._unique = False
User._meta.get_field('telegram_chat_id')._unique = True

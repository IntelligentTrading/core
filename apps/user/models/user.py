import uuid
import logging
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.behaviors import Timestampable


(LOW_RISK, MEDIUM_RISK, HIGH_RISK) = list(range(3))
RISK_CHOICES = (
    (LOW_RISK, 'low'),
    (MEDIUM_RISK, 'medium'),
    (HIGH_RISK, 'high'),
)

(SHORT_HORIZON, MEDIUM_HORIZON, LONG_HORIZON) = list(range(3))
HORIZON_CHOICES = (
    (SHORT_HORIZON, 'short'),
    (MEDIUM_HORIZON, 'medium'),
    (LONG_HORIZON, 'long'),
)


class User(AbstractUser, Timestampable):
    USERNAME_FIELD = 'telegram_chat_id'
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS
    REQUIRED_FIELDS.remove('email')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    telegram_chat_id = models.CharField(max_length=128, null=False, unique=True)
    is_subscribed = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)

    risk = models.SmallIntegerField(choices=RISK_CHOICES, default=LOW_RISK)
    horizon = models.SmallIntegerField(choices=HORIZON_CHOICES, default=MEDIUM_HORIZON)


    # MODEL PROPERTIES


    # MODEL FUNCTIONS

    def get_risk_value(self, display_string=None):
        if not display_string:
            display_string = self.get_risk_display()
        return get_risk_value_from_string(display_string)

    def get_horizon_value(self, display_string=None):
        if not display_string:
            display_string = self.get_horizon_display()
        return get_horizon_value_from_string(display_string)

    def get_telegram_settings(self):
        return {
            'is_subscribed': self.is_subscribed,
            'is_muted': self.is_muted,
            'risk': self.get_risk_display(),
            'horizon': self.get_horizon_display()
        }

User._meta.get_field('username')._unique = False
User._meta.get_field('telegram_chat_id')._unique = True


def get_risk_value_from_string(display_string):
    if display_string == 'low':
        return LOW_RISK
    elif display_string == 'medium':
        return MEDIUM_RISK
    elif display_string == 'high':
        return HIGH_RISK
    else:
        raise Exception("unrecognized risk string provided")


def get_horizon_value_from_string(display_string):
    if display_string == 'short':
        return SHORT_HORIZON
    elif display_string == 'medium':
        return MEDIUM_HORIZON
    elif display_string == 'long':
        return LONG_HORIZON
    else:
        raise Exception("unrecognized horizon string provided")

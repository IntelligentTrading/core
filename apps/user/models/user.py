import uuid
import logging

from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.behaviors import Timestampable
import os


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
    is_muted = models.BooleanField(default=False)

    risk = models.SmallIntegerField(choices=RISK_CHOICES, default=LOW_RISK)
    horizon = models.SmallIntegerField(choices=HORIZON_CHOICES, default=MEDIUM_HORIZON)

    _beta_subscription_token = models.CharField(max_length=8, null=True, unique=True)
    subscribed_since = models.DateTimeField(null=True)


    # MODEL PROPERTIES
    @property
    def is_subscribed(self):
        return True if self.subscribed_since else False

    @is_subscribed.setter
    def is_subscribed(self, value):
        if value and not self.subscribed_since:
            self.subscribed_since = datetime.now()
        elif not value:
            self.subscribed_since = None


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
            'beta_token_valid': bool(self._beta_subscription_token),
            'is_muted': self.is_muted,
            'risk': self.get_risk_display(),
            'horizon': self.get_horizon_display()
        }

    def set_subscribe_token(self, token):
        A_PRIME_NUMBER = os.environ.get('A_PRIME_NUMBER')
        if int(token, 16) % A_PRIME_NUMBER == 0:
            # check no other users using the same token
            if not User.objects.filter(_beta_subscription_token=token).count():
                self._beta_subscription_token = token


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

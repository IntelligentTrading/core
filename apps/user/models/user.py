import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from apps.common.behaviors import Timestampable


class User(AbstractUser, Timestampable):
    USERNAME_FIELD = 'telegram_chat_id'
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS
    REQUIRED_FIELDS.remove('email')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    telegram_chat_id = models.CharField(max_length=128, null=False)


    # MODEL PROPERTIES


    # MODEL FUNCTIONS


User._meta.get_field('username')._unique = False
User._meta.get_field('telegram_chat_id')._unique = True

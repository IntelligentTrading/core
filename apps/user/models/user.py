import uuid
from django.db import models
from apps.common.behaviors import Timestampable


class User(Timestampable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    telegram_chat_id = models.CharField(max_length=128, null=False)


    # MODEL PROPERTIES


    # MODEL FUNCTIONS

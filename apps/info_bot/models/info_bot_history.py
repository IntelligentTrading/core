from django.db import models
from unixtimestampfield.fields import UnixTimeStampField



class InfoBotHistory(models.Model):
    """ Log replies from the Telegram """
    update_id = models.IntegerField(null=True)
    group_chat_id = models.IntegerField(null=True)
    user_chat_id = models.IntegerField(null=True)
    username = models.CharField(max_length=32, default="")
    bot_command_text = models.CharField(max_length=64, default="")
    language_code = models.CharField(max_length=8, default="")
    datetime = UnixTimeStampField(null=False)

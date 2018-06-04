import logging
import schedule
import time
import threading

from django.core.management.base import BaseCommand

from apps.info_bot.telegram.start_info_bot import start_info_bot



logger = logging.getLogger(__name__)

# Set via @BotFather:
# can be added to groups, has access to all messages
#
# https://core.telegram.org/bots/faq#what-messages-will-my-bot-get

class Command(BaseCommand):
    help = 'Run basic telegram info bot'

    def handle(self, *args, **options):
        logger.info("Starting telegram info_bot.")

        start_info_bot()
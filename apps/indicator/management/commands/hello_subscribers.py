import logging

from django.core.management.base import BaseCommand

from apps.indicator.telegram_alert import TelegramAlert

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send a friendly greeting to all our subscribers."

    def handle(self, *args, **options):
        logger.info("Let's say hello to our subscribers...")
        alert = TelegramAlert(text="Hello traders! 😺 \n Did you buy Bitcoin today?")
        alert.send()

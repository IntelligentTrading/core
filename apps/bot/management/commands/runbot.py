import logging

from django.core.management.base import BaseCommand

from apps.bot.telegram.startbot import startbot


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run basic telegram info bot'

    def handle(self, *args, **options):
        logger.info("Starting telegram info bot.")
        startbot()
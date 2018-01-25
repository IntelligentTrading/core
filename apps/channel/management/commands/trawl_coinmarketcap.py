import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Basic data bot"

    def handle(self, *args, **options):
        logger.info("Getting ready to do stuff...")

        # do stuff


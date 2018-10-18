import logging

from django.core.management.base import BaseCommand

from apps.TA.storages.data.memory_cleaner import redisCleanup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Cleanup for TA Storages on Redis'

    def handle(self, *args, **options):
        logger.info("Starting TA cache clean.")

        redisCleanup()

        from settings.redis_db import database
        if int(database.info()['used_memory']) > (2 ** 30 * .9):
            # todo: some major alert to upgrade the cache memory
            pass

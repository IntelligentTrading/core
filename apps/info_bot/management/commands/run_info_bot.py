import logging
import schedule
import time
import threading

from django.core.management.base import BaseCommand

from apps.info_bot.telegram.start_info_bot import start_info_bot
from apps.info_bot.telegram.bot_commands.itt import precache_currency_info

from apps.info_bot import tasks

from settings import INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS

logger = logging.getLogger(__name__)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

class ScheduleThread(threading.Thread):
    def __init__(self, *pargs, **kwargs):
        # daemon=true so when your program quits, any daemon threads are killed automatically
        super().__init__(*pargs, daemon=True, name="scheduler", **kwargs)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(schedule.idle_seconds())

# Set via @BotFather:
# inline mode, can be added to groups, has access to all messages
#
# https://core.telegram.org/bots/faq#what-messages-will-my-bot-get

class Command(BaseCommand):
    help = 'Run basic telegram info bot'

    def handle(self, *args, **options):
    
        logger.info('Precaching info for telegram info_bot')
        #run_threaded(precache_currency_info)
        tasks.precache_currency_info_for_info_bot.delay()
        schedule.every(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS).seconds.do(
        #    run_threaded, precache_currency_info
            tasks.precache_currency_info_for_info_bot.delay
        )
        ScheduleThread().start()

        logger.info("Starting telegram info_bot.")
        start_info_bot()
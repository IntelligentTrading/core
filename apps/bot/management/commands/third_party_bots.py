import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import schedule
import time
from commands.command_index import unknown_command

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Basic data bot"

    def handle(self, *args, **options):
        logger.info("Getting ready to do stuff...")

        updaters = dispatchers = {}

        for bot in TelegramBot.objects.filter(token__isnull=False):
            updaters[bot.id] = Updater(token=bot.token)
            dispatchers[bot.id] = updaters[bot.id].dispatcher

            # UNKNOWN-COMMAND HANDLER
            unknown_handler = MessageHandler(Filters.command, unknown_command)
            dispatchers[bot.id].add_handler(unknown_handler)

            updaters[bot.id].start_polling()
            updaters[bot.id].idle()


            # do stuff


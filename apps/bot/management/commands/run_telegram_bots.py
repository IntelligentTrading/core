import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import schedule
import time

from apps.bot.models import TelegramBot
from apps.bot.telegram import bot_commands_index
from apps.bot.telegram.bot_commands_index import unknown_command

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Basic data bot"

    def handle(self, *args, **options):
        logger.info("Getting ready to do stuff...")
        updaters = dispatchers = {}

        # for bot in TelegramBot.objects.filter(token__isnull=False):
        for bot in TelegramBot.objects.filter(name="ITT Info Bot"): #ONLY ONE FOR NOW
            # POLLING HANGS THE PROCESS AND THIS LOOP WILL NOT CONTINUE TO INITIALIZE THE NEXT BOT

            updaters[bot.id] = Updater(token=bot.token)
            dispatchers[bot.id] = updaters[bot.id].dispatcher

            # REGISTER HANDLERS FOR ALL COMMANDS
            for command in bot_commands_index.commands:
                try:
                    dispatchers[bot.id].add_handler(
                        CommandHandler(command.execution_handle,
                                       command,
                                       pass_args=command.pass_args)
                    )
                except Exception as e:
                    print("Error adding handler to bot " + bot.id + ": " + str(e))


            # UNKNOWN-COMMAND HANDLER
            unknown_handler = MessageHandler(Filters.command, unknown_command)
            dispatchers[bot.id].add_handler(unknown_handler)

            updaters[bot.id].start_polling()
            updaters[bot.id].idle()

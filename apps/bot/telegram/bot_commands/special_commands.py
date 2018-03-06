""" Special commands:

help - list of available commands

restart - restart bot
start - first greeting from bot
"""

import logging
import os
import sys
from threading import Thread
from textwrap import dedent

from telegram import ParseMode
from telegram.ext import Updater

from settings import TELEGRAM_BOT_API_TOKEN



logger = logging.getLogger(__name__)

## bot admin commands

updater = Updater(token=TELEGRAM_BOT_API_TOKEN)

def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

def restart(bot, update):
    update.message.reply_text('itt bot is restarting...')
    Thread(target=stop_and_restart).start()


## special commands

def unknown(bot, update):
    update.message.reply_text(dedent("""
        Sorry {}, I don't understand this, please check the list of available commands with `/help`.
        Or just type: `/itt BTC` to check info about Bitcoin.
        """).format(update.message.from_user.first_name), parse_mode=ParseMode.MARKDOWN)

def start(bot, update):
    update.message.reply_text("Welcome {}. I'm ITT info bot.".format(update.message.from_user.first_name))

def help(bot, update):
    update.message.reply_text(dedent("""
        Here's a list of all commands currently available:

        /help - Get a list of all commands
        /itt - Short info about currency. For example: `/itt BTC`
    """), ParseMode.MARKDOWN)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
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

from apps.info_bot.helpers import save_history#, restore_db_connection

from settings import INFO_BOT_TELEGRAM_BOT_API_TOKEN, LOCAL



logger = logging.getLogger(__name__)

## bot admin commands

if LOCAL:
    updater = Updater(token=INFO_BOT_TELEGRAM_BOT_API_TOKEN)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        update.message.reply_text('itf bot is restarting...')
        Thread(target=stop_and_restart).start()


## special commands

def unknown(bot, update):
    update.message.reply_text(dedent("""
        Sorry {}, I don't understand this, please check the list of available commands with `/help`.
        Or just type: `/itf BTC` to check info about Bitcoin.
        """).format(update.message.from_user.first_name), parse_mode=ParseMode.MARKDOWN)

@restore_db_connection
def start(bot, update):
    save_history(update)
    update.message.reply_text("Welcome {}. I'm ITF info bot.".format(update.message.from_user.first_name))

#@restore_db_connection
def help(bot, update):
    save_history(update)
    update.message.reply_text(dedent("""
        *Available commands:*

        *•* `/itf <cryptocurrency>` - Info about currency. For example: `/itf BTC` or `/itf XRP_ETH`.
        *•* `/i <cryptocurrency>` - Latest info about price and volume.
        *•* `/ta <cryptocurrency>` - Latest TA alerts for currency.
        *•* `/s <cryptocurrency>` - Latest crowd sentiment alert for currency.
        *•* `/price <cryptocurrency>` - Prices from all exchanges.
        *•* `/info` - List of supported coins and exchanges.
        *•* `/help` - List of all commands.

        To use these commands in your Telegram channel, invite @Intelligent\_Trading\_Info\_Bot to your channel.
    """), ParseMode.MARKDOWN)

def getme(bot, update):
    "Show username and userid in chat"
    save_history(update)
    update.message.reply_text(f"Your username:{update.message.from_user.username} and userId {str(update.message.from_user.id)}")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

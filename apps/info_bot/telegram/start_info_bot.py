"""
python-telegram-bot:
https://github.com/python-telegram-bot/python-telegram-bot

Telegram API:
https://core.telegram.org/bots/api
"""
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import InlineQueryHandler

from apps.info_bot.telegram.bot_commands import itt
from apps.info_bot.telegram.bot_commands import inline
from apps.info_bot.telegram.bot_commands import special_commands

from settings import LOCAL, INFO_BOT_TELEGRAM_BOT_API_TOKEN, INFO_BOT_ADMIN_USERNAME

logger = logging.getLogger(__name__)



# too much DEBUG messages from telegram
logging.getLogger("telegram.bot").setLevel(logging.INFO)
logging.getLogger("telegram.vendor").setLevel(logging.INFO)

def start_info_bot():
    updater = Updater(token=INFO_BOT_TELEGRAM_BOT_API_TOKEN)

    # Dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', special_commands.start))
    dp.add_handler(CommandHandler('help', special_commands.help))

    dp.add_handler(CommandHandler('itt', itt.itt, pass_args=True))

    if LOCAL:
        dp.add_handler(CommandHandler('r', special_commands.restart, \
            filters=Filters.user(username=INFO_BOT_ADMIN_USERNAME)))

    # inline mode
    dp.add_handler(InlineQueryHandler(inline.inlinequery))

    # log all errors
    dp.add_error_handler(special_commands.error)

    # handle unkomwn commands
    # this handler must be added last.
    dp.add_handler(MessageHandler(Filters.command, special_commands.unknown))

    logger.info("All handlers added to the telegram info_bot.")

    updater.start_polling()
    updater.idle()

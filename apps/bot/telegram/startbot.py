"""
python-telegram-bot:
https://github.com/python-telegram-bot/python-telegram-bot

Telegram API:
https://core.telegram.org/bots/api

Bot url:
telegram.me/AlienTestBot

"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import InlineQueryHandler

from settings import TELEGRAM_BOT_API_TOKEN, LOCAL

from apps.bot.telegram.bot_commands import itt
from apps.bot.telegram.bot_commands import inline

from apps.bot.telegram.bot_commands import special_commands



def startbot():
    updater = Updater(token=TELEGRAM_BOT_API_TOKEN)

    # Dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', special_commands.start))
    dp.add_handler(CommandHandler('help', special_commands.help))

    dp.add_handler(CommandHandler('itt', itt.itt, pass_args=True))

    if LOCAL:
        dp.add_handler(CommandHandler('r', special_commands.restart, filters=Filters.user(username='@lexusnexus')))

    # inline mode
    dp.add_handler(InlineQueryHandler(inline.inlinequery))

    # log all errors
    dp.add_error_handler(special_commands.error)

    # this handler must be added last.
    dp.add_handler(MessageHandler(Filters.command, special_commands.unknown)) # handler for unkomwn commands

    updater.start_polling()
    updater.idle()

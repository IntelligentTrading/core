from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode

from apps.bot.telegram.bot_commands.itt import ALL_COINS
from apps.bot.telegram.bot_commands.itt import currency_info

from settings import LOCAL


# This bot works automatically, no need to add it anywhere.
# Simply open any of your chats and type @botname <currency>. Then tap on the result.

def inlinequery(bot, update):
    results = list()
    query = update.inline_query.query.upper() # BTC, ETH
#    currencies = (coin for coin in ALL_COINS if coin.startswith(query))
    results = [
        InlineQueryResultArticle(
            id='help',
            title="Get info on popular cryptocurrencies",
            description="Enter `BTC` or `ETH`. And tap here.",
            thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
            input_message_content=InputTextMessageContent("Enter *@AlienTestBot BTC* to get current info about Bitcoin", ParseMode.MARKDOWN)
        )
    ]
    if query in ALL_COINS:
        currency = query
        results = list()
        message_text = currency_info(currency)
        results = [
            InlineQueryResultArticle(
                id=currency,
                title="Get info on {}".format(currency),
                description="Tap here to get info on {}".format(currency),
                thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
                input_message_content=InputTextMessageContent(message_text, ParseMode.MARKDOWN, disable_web_page_preview=True),
            )
        ]
    if LOCAL:
        update.inline_query.answer(results, cache_time=2) # cache_time in seconds
    else:
        update.inline_query.answer(results) # default cache_time is 300 seconds

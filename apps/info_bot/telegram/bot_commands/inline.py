"""
Bot in inline mode works automatically, no need to add it anywhere.
Simply open any of your chats and type @botname <currency>. Then tap on the result.
"""

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode

#from apps.info_bot.telegram.bot_commands.itf import ALL_COINS
#from apps.info_bot.telegram.bot_commands.itf import currency_info

from settings import LOCAL



def inlinequery(bot, update):
    results = list()
    # query = update.inline_query.query.upper() # BTC, ETH
    # results = [
    #     InlineQueryResultArticle(
    #         id='help',
    #         title="Get info on popular cryptocurrencies",
    #         description="Enter `BTC` or `ETH`. And tap here.",
    #         # FIXME replace hardcoded thumb_url
    #         thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
    #         input_message_content=InputTextMessageContent("Enter *@AlienTestBot BTC* to get current info about Bitcoin", ParseMode.MARKDOWN)
    #     )
    # ]
    # if query in ALL_COINS:
    #     currency = query
    #     results = list()
    #     message_text = currency_info(currency)
    #     results = [
    #         InlineQueryResultArticle(
    #             id=currency,
    #             title="Get info on {}".format(currency),
    #             description="Tap here to get info on {}".format(currency),
    #             # FIXME replace hardcoded thumb_url
    #             thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
    #             input_message_content=InputTextMessageContent(message_text, ParseMode.MARKDOWN, disable_web_page_preview=True),
    #         )
    #     ]
    # if LOCAL:
    #     update.inline_query.answer(results, cache_time=2) # 2 seconds for debug
    # else:
    #     update.inline_query.answer(results) # by default telegram cache reply for 300 seconds

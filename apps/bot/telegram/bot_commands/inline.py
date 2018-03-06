from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode

from apps.bot.telegram.bot_commands.itt import ALL_COINS
from apps.bot.telegram.bot_commands.itt import currency_info



def inlinequery(bot, update):
    results = list()
    query = update.inline_query.query.upper() # BTC, ETH
    currencies = (coin for coin in ALL_COINS if coin.startswith(query))
    results = [
        InlineQueryResultArticle(
            id='help',
            title="Get info on popular cryptocurrencies",
            description="Enter `BTC` or `ETH`",
            thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
            input_message_content=InputTextMessageContent("Enter *@AlienTestBot BTC* to get current info about Bitcoin", ParseMode.MARKDOWN)
        )
    ]
    if query in ALL_COINS:
        currency = query
        results = list()
        message_text = currency_info(currency)
        results.append(
            InlineQueryResultArticle(
                id=currency,
                title="Get info on {}".format(currency),
                description="Get info on {}".format(currency),
                thumb_url="https://token-sale.intelligenttrading.org/assets/img/icons/apple-touch-icon-152x152.png",
                input_message_content=InputTextMessageContent(message_text, ParseMode.MARKDOWN),
            )
        )
    update.inline_query.answer(results, cache_time=2)

# def inlinequery(bot, update):
#     query = update.inline_query.query.upper()
#     if not query:
#         currencies = ('BTC','ETH', 'DASH')
#     else:
#         currencies = [coin for coin in ALL_COINS if coin.startswith(query)]
#     results = []
#     # find all coins that start with query
#     coins = [coin for coin in ALL_COINS if coin.startswith(query)]
#     for coin in coins:
#         results.append(
#             InlineQueryResultArticle(
#                 id=coin,
#                 title=coin,
#                 input_message_content=InputTextMessageContent(
#                     "*{}* the best".format(coin),
#                     parse_mode=ParseMode.MARKDOWN),
#                 thumb_height=1,
#             )
#         )
#     update.inline_query.answer(results)

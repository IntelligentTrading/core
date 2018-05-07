""" Commands:

arbitrage - Show price for the trading pair at the different exchanges. For example: /arbitrage BTC_USDT
"""

import math
import requests
from datetime import datetime, timedelta

from cache_memoize import cache_memoize
from telegram import ParseMode

from settings import INFO_BOT_CRYPTOPANIC_API_TOKEN, INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS
from settings import COUNTER_CURRENCIES

from apps.indicator.models import Price, Volume
from apps.signal.models import Signal

from taskapp.helpers import get_source_name

from apps.info_bot.helpers import parse_trading_pair_string, get_currency_pairs
from apps.info_bot.helpers import default_counter_currency_for, trading_pairs_for


## user commands
def arbitrage(bot, update, args):
    view = "Arbitrage is not implemented yet. This is just stub\n\n"
    view += "*BTC*_USDT. From the lowest price:\n\n"
    view += "Bittrex: $9724.00 (2018-05-04 13:29:02 UTC)\n"
    view += "Poloniex: $9726.00 (2018-05-04 13:30:02 UTC)\n"
    view += "Binance: $9728.00 (2018-05-04 13:31:34 UTC)\n"
    update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

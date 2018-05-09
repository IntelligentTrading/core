""" 
Commands:
/price - Show price for the trading pair at the different exchanges. For example: /price BTC_USDT
"""

import math
from datetime import datetime, timedelta
import requests

from cache_memoize import cache_memoize
from telegram import ParseMode

from settings import INFO_BOT_CRYPTOPANIC_API_TOKEN, INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS
from settings import COUNTER_CURRENCIES, LOCAL

from apps.indicator.models import Price, Volume
from apps.signal.models import Signal

from taskapp.helpers import get_source_name, get_exchanges

from apps.info_bot.helpers import parse_trading_pair_string, get_currency_pairs
from apps.info_bot.helpers import default_counter_currency_for, trading_pairs_for
from apps.info_bot.helpers import natural_join

from apps.info_bot.telegram.bot_commands.itt import format_currency, format_timestamp



def price_view(trading_pair):
    view = ''

    if trading_pair['counter_currency'] == 'USDT':
        currency_symbol = '$'
    else:
        currency_symbol = ''

    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    exchanges = get_exchanges()

    # Prices 
    last_prices_object = Price.objects.filter(
        source__in = exchanges,
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp')[:len(exchanges)]


    seen = set()
    seen_add = seen.add
    # remove dublicates
    unique_last_prices = [price for price in last_prices_object if not (price.source in seen or seen_add(price.source))]
    exchanges_with_price = natural_join([get_source_name(price.source).title() for price in unique_last_prices])

    view += f"I found *{currency}*\_{trading_pair['counter_currency']} in {exchanges_with_price}\n"

    for price_obj in sorted(unique_last_prices, key=lambda pr: pr.price):
        view += f"\n*{format_currency(price_obj.price, currency_symbol)}* on {get_source_name(price_obj.source).title()} at {format_timestamp(price_obj.timestamp)}"

    return view



## user commands
def price(bot, update, args):
    try:
        arg = args[0].upper()
    except:
        update.message.reply_text("Please add coin abbreviation or trading pair to command. For example: `/price BTC` or `/price ETH_USDT`", ParseMode.MARKDOWN)
        return

    period_in_seconds = 2*60*60 if not LOCAL else 2000*60*60

    trading_pairs_available = get_currency_pairs(source='all', period_in_seconds=period_in_seconds, counter_currency_format="text")
    trading_pair = parse_trading_pair_string(arg)

    # wrong arg format
    if trading_pair['transaction_currency'] == trading_pair['counter_currency'] == None:
        view = f"Sorry, I can't understand this coin format: `{args[0]}`. Please enter: `/price BTC` or `/price ETH_USDT`"

    # we don have info on this coin
    elif trading_pair['counter_currency'] == None:
        trading_pair['counter_currency'] = default_counter_currency_for(trading_pair['transaction_currency'], trading_pairs_available)
        if trading_pair['counter_currency'] == None:
            coins = set(coin for coin, _ in trading_pairs_available)
            view = f"Sorry, I don't support `{trading_pair['transaction_currency']}`\n\nPlease use one of this coins:\n\n{', '.join(coins)}.\n\nOr just enter `/price BTC` or `/price ETH_USDT`"
        else:
            view = price_view(trading_pair)
    # wrong counter currency
    elif (trading_pair['transaction_currency'], trading_pair['counter_currency']) not in trading_pairs_available:
        good_trading_pairs = "` or `".join([f"{tc}_{cc}" for (tc, cc) in trading_pairs_for(trading_pair['transaction_currency'], trading_pairs_available)])
        view = f"Sorry, I don't support this trading pair `{trading_pair['transaction_currency']}_{trading_pair['counter_currency']}`\n\n"
        if good_trading_pairs:
            view += f"Please use: `{good_trading_pairs}`"

    # all good and well
    else:
        view = price_view(trading_pair)

    update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return




    view = "Arbitrage is not implemented yet. This is just stub\n\n"
    view += "*BTC*_USDT. From the lowest price:\n\n"
    view += "Bittrex: $9724.00 (2018-05-04 13:29:02 UTC)\n"
    view += "Poloniex: $9726.00 (2018-05-04 13:30:02 UTC)\n"
    view += "Binance: $9728.00 (2018-05-04 13:31:34 UTC)\n"
    update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

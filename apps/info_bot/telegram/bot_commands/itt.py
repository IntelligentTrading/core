""" Commands:

itt - Short info about currency. For example: /itt BTC
"""

import math
import requests
from textwrap import dedent
from datetime import datetime, timedelta

from cache_memoize import cache_memoize
from telegram import ParseMode

from django.core.cache import cache

from settings import INFO_BOT_CRYPTOPANIC_API_TOKEN, INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS
from settings import USDT_COINS, BTC_COINS, BTC, USDT

from apps.indicator.models import Price, Volume
from apps.signal.models import Signal


# combine and remove dublicates, USDT_COINS first in list
ALL_COINS = USDT_COINS + list(set(BTC_COINS)-set(USDT_COINS))
POPULAR_COINS = ('BTC', 'DASH', 'ETH', 'LTC', 'XMR', 'XRP', 'ZEC')

## helpers

def percents(new_value, old_value):
    return (100*(new_value - old_value)/old_value)

def diff_symbol(diff): # ↑ increase, ↓ decrease
    if diff > 0:
        d_sym = "↑"
    elif diff < 0:
        d_sym = "↓"
    else:
        d_sym = ""
    return d_sym

def format_timestamp(timestamp):
    return timestamp.strftime('%b %d, %H:%M')

def format_currency(amount, currency_symbol='', in_satoshi=True):
    if amount == 0:
        return currency_symbol + '0.00'

    if in_satoshi: # convert from satoshis
        amount = float(amount * float(10**-8))

    common_logarithm = int(math.log10(abs(amount)))
    if common_logarithm > 3: # 12345.2212 -> 12345
        currency_norm = "{:.0f}".format(amount)
    elif common_logarithm > 0: # 123.2212 -> 123.22
        currency_norm = "{:.2f}".format(amount)
    else: # 0.123400000 -> 0.1234
        currency_norm = "{:.6f}".format(amount).rstrip('0').rstrip('.')

    return currency_symbol + currency_norm

def sentiment_from_cryptopanic(currency):
    INFO_BOT_CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/posts/?auth_token={}&filter=trending&currencies={}".format(
        INFO_BOT_CRYPTOPANIC_API_TOKEN, currency)
    try:
        data = requests.get(INFO_BOT_CRYPTOPANIC_API_URL).json()
        last_result = data['results'][0]
        title = last_result['title']
        link = last_result['url']
    except:
        title, link = '', ''
    return (title, link)


# Attach decorator to cacheable function. Now: 3 hours.
@cache_memoize(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS)
def currency_info(currency):
    if currency in USDT_COINS:
        counter_currency = USDT
        counter_currency_txt = 'USDT'
        currency_symbol = '$'
    else:
        counter_currency = BTC
        counter_currency_txt = 'BTC'
        currency_symbol = ''

    # Price
    price_new_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp').first()

    price_24h_old_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency,
        timestamp__lte=price_new_object.timestamp - timedelta(minutes=1440)
        ).order_by('-timestamp').first()

    percents_price_diff_24h = percents(price_new_object.price, price_24h_old_object.price)

    price_section = "*{}*/{} *{} {}*\n24hr Change: {}".format(
        currency, counter_currency_txt, format_currency(price_new_object.price, currency_symbol),
        diff_symbol(percents_price_diff_24h), '{:+.2f}%'.format(percents_price_diff_24h)
    )

    # Volume
    volume_object = Volume.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency,
        ).order_by('-timestamp').first()
    volume_section = "\n24hr Volume: {} {}".format(format_currency(volume_object.volume, in_satoshi=False), counter_currency_txt)

    # Signals
    last_signals = []

    for signal in ['SMA', 'RSI']:
        signal_object = Signal.objects.filter(
            transaction_currency=currency, counter_currency=counter_currency,
            signal=signal
            ).order_by('-timestamp').first()
        last_signals.append(signal_object)

    signals_section = '\n\n*Latest signals:*'
    for signal in sorted(last_signals, key=lambda s: s.timestamp, reverse=True):
        signals_section+= "\n{} {} {}".format(format_timestamp(signal.timestamp), \
                            signal.signal, format_currency(signal.price))

    itt_dashboard_url = 'http://intelligenttrading.org/'
    more_info_section = "\n[Get more signals on ITT Dashboard]({})".format(itt_dashboard_url)

    # Sentiments from cryptopanic
    (title, url) = sentiment_from_cryptopanic(currency)
    if '' not in (title, url):
        cryptopanic_sentiment_section = "\n\n\"{}\"\n[Read on CryptoPanic]({})".format(title, url)
    else:
        cryptopanic_sentiment_section = ""

    reply_text = price_section + volume_section + signals_section + \
                    more_info_section + cryptopanic_sentiment_section

    return reply_text


## utility functions

def precache_currency_info():
    for currency in POPULAR_COINS:
        currency_info(currency, _refresh=True) # "heat the cache up" right after we've cleared it


## user commands

def itt(bot, update, args):
    try:
        currency = args[0].upper()
    except:
        update.message.reply_text("Please add currency abbreviation to command. For example: `/itt BTC`", ParseMode.MARKDOWN)
        return

    if currency in ALL_COINS:
        reply_text = currency_info(currency)
    else:
        reply_text = "Sorry, I know nothing about this currency `{}`.\nPlease use one of this:\n\n{}.".format(args[0].upper(), ", ".join(ALL_COINS))

    update.message.reply_text(reply_text, ParseMode.MARKDOWN, disable_web_page_preview=True)

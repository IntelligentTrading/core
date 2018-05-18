""" Commands:

itt - Short info about currency. For example: /itt BTC, /itt OMG_ETH
"""
from datetime import timedelta
import requests

from cache_memoize import cache_memoize
from telegram import ParseMode

from settings import INFO_BOT_CRYPTOPANIC_API_TOKEN, INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS
from settings import COUNTER_CURRENCIES

from apps.indicator.models import Price, Volume
from apps.signal.models import Signal

from apps.info_bot.helpers import format_currency, format_timestamp, parse_telegram_cryptocurrency_args

from taskapp.helpers import get_source_name



# combine and remove dublicates, USDT_COINS first in list
#POPULAR_COINS = ('BTC', 'DASH', 'ETH', 'LTC', 'XMR', 'XRP', 'ZEC')

## helpers

def percents(new_value, old_value):
    return (100*(new_value - old_value)/old_value)

def diff_symbol(diff): # ↑ increase, ↓ decrease
    if diff > 0:
        d_sym = "⬆"
    elif diff < 0:
        d_sym = "⬇"
    else:
        d_sym = ""
    return d_sym

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


## utility functions

# def precache_currency_info():
#     for currency in POPULAR_COINS:
#         currency_info(currency, _refresh=True) # "heat the cache up" right after we've cleared it


## New helpers
@cache_memoize(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS)
def itt_view(trading_pair):
    view = ''

    if trading_pair['counter_currency'] == 'USDT':
        currency_symbol = '$'
    else:
        currency_symbol = ''

    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    # Price section
    price_new_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp').first()

    source = price_new_object.source
    price_24h_old_object = Price.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        timestamp__lte=price_new_object.timestamp - timedelta(minutes=1440)
        ).order_by('-timestamp').first()

    percents_price_diff_24h = percents(price_new_object.price, price_24h_old_object.price)

    view += f"*{currency}*\_{trading_pair['counter_currency']} *{format_currency(price_new_object.price, currency_symbol)}*"
    view += f" *{diff_symbol(percents_price_diff_24h)}*\n24hr Change: {'{:+.2f}%'.format(percents_price_diff_24h)}"

    # Volume section
    volume_object = Volume.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        ).order_by('-timestamp').first()
    view += f"\nVolume: {format_currency(volume_object.volume, in_satoshi=False)} {trading_pair['counter_currency']}"

    # Source (maybe show time in user local time not in UTC) and last update
    view += f"\n\nSource: {get_source_name(source).capitalize()}"
    view += f"\nLast update: {price_new_object.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"

    try:
    # Signals
        latest_signals = list()
        for signal in ['SMA', 'RSI', 'RSI_Cumulative']:
            signal_object = Signal.objects.filter(
                source=source, transaction_currency=currency, counter_currency=counter_currency,
                signal=signal
                ).order_by('-timestamp').first()
            latest_signals.append(signal_object)

        view += f"\n\n*Latest signals*"

        trend_labels = ['overbought', 'neutral', 'oversold']
        for signal in sorted(latest_signals, key=lambda s: s.timestamp, reverse=True):
            general_trend = 'Bullish' if signal.trend == 1 else 'Bearish'
            if signal.signal == 'RSI':
                view += f"\n *•* {format_timestamp(signal.timestamp)} {general_trend} *{signal.signal}* ({int(signal.rsi_value)}), {trend_labels[int(signal.trend)+1]} for {signal.get_horizon_display()} horizon. Price {format_currency(signal.price, currency_symbol)}."
            elif signal.signal == 'RSI_Cumulative':
                view += f"\n *•* {format_timestamp(signal.timestamp)} {general_trend} *ITF Proprietary Alert*, {trend_labels[int(signal.trend)+1]} for {signal.get_horizon_display()} horizon. Price {format_currency(signal.price, currency_symbol)}."
            elif signal.signal == 'SMA':
                view += f"\n *•* {format_timestamp(signal.timestamp)} {general_trend} *{signal.signal}* ({format_currency(signal.price, currency_symbol)}), {trend_labels[int(signal.trend)+1]} for {signal.get_horizon_display()} horizon. Price {format_currency(signal.price, currency_symbol)}."

        itf_more_info_url = 'http://intelligenttrading.org/features/'
        view += f"\n\n[Get more signals on ITF website]({itf_more_info_url})"
#        view += f" or [Ask our representative](tg://user?id=458693263)"
    except: # no signals
        pass

    # Sentiments from cryptopanic
    (title, url) = sentiment_from_cryptopanic(currency)
    if '' not in (title, url):
        view += f"\n\n\"{title}\"\n[Read on CryptoPanic]({url})"

    return view

## user commands
def itt(bot, update, args):
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='itt')
    if trading_pair:
        view = itt_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

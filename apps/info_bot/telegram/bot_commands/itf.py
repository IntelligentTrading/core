""" Commands:

itf - Short info about currency. For example: /itf BTC, /itf OMG_ETH
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
from apps.info_bot.helpers import save_history, restore_db_connection

from taskapp.helpers import get_source_name



# combine and remove dublicates, USDT_COINS first in list
#POPULAR_COINS = ('BTC', 'DASH', 'ETH', 'LTC', 'XMR', 'XRP', 'ZEC')

## helpers

def percents(new_value, old_value):
    return 100*(new_value - old_value)/old_value

def diff_symbol(diff): # ↑ increase, ↓ decrease
    if diff > 0:
        d_sym = "⬆"
    elif diff < 0:
        d_sym = "⬇"
    else:
        d_sym = ""
    return d_sym

@cache_memoize(4*60*60) # 4 hours
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

# signal templates
# https://github.com/IntelligentTrading/ui/blob/master/util/signal-helper.js
def get_rsi_template(signal):
    trend = int(signal.trend)
    strength_value = int(signal.strength_value) if signal.strength_value else 1
    #print(f"trading_pair tc:{signal.transaction_currency} cc:{signal.counter_currency} signal: {signal.signal}, trend: {trend} ({type(trend)}, strenght:{signal.strength_value}({type(signal.strength_value)}")
    rsi_emoji = '⚠️' if trend == 1 else '🆘'
    rsi_strength_values = ['', 'Very ', 'Extremely ']
    rsi_trend = ['Overbought', 'Neutral', 'Oversold']

    rsi = {
        'rsi_header_emoji': 'ℹ️',
        'rsi_header_emoji_pro': '🔰',
        'premium': 'ITF Proprietary Alert',
    }
    rsi['rsi_text'] = f"RSI: *{rsi_strength_values[strength_value - 1]}{rsi_trend[trend + 1]}* ({int(signal.rsi_value)}) {rsi_emoji}"

    if trend == 1:
        rsi['rsi_general_trend'] = "Bullish"
        rsi['rsi_itt_bias'] = "Trend reversal to the *upside* is near."
    else:
        rsi['rsi_general_trend'] = "Bearish"
        rsi['rsi_itt_bias'] = "Trend reversal to the *downside* is near."
    return rsi


def get_kumo_template(signal):
    trend = int(signal.trend)
    ichi_emoji = '🆘' if trend == -1  else '✅'
    ichi_breakout = 'Negative' if trend == -1 else 'Positive'
    ichi_bias = 'Bear' if trend == -1 else 'Bull'

    return {
        'ichimoku_header_emoji': 'ℹ️',
        'ichimoku_text': f'Ichimoku: {ichi_breakout} Cloud Breakout {ichi_emoji}\nITF Bias: {ichi_bias} trend continuation likely.'
    }

## utility functions

# def precache_currency_info():
#     for currency in POPULAR_COINS:
#         currency_info(currency, _refresh=True) # "heat the cache up" right after we've cleared it


## New helpers
@cache_memoize(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS) # 1 hours
def itf_view(trading_pair):
    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    # Price
    price_new_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp').first()

    source = price_new_object.source
    view = f"*{currency}*\_{trading_pair['counter_currency']} *{format_currency(price_new_object.price, trading_pair['counter_currency'])}*"

    price_24h_old_object = Price.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        timestamp__lte=price_new_object.timestamp - timedelta(minutes=1440)
        ).order_by('-timestamp').first()
    try:
        percents_price_diff_24h = percents(price_new_object.price, price_24h_old_object.price)
        view += f" *{diff_symbol(percents_price_diff_24h)}*\n24hr Change: {'{:+.2f}%'.format(percents_price_diff_24h)}"
    except:
        view += "\n"

    # Volume
    volume_object = Volume.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        ).order_by('-timestamp').first()
    view += f"\nVolume: {format_currency(amount=volume_object.volume, currency_symbol=currency, in_satoshi=False)}"

    # Source (maybe show time in user local time not in UTC) and last update
    view += f"\n\nSource: {get_source_name(source).capitalize()}"
    view += f"\nLast update: {price_new_object.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"

    # Signals
    latest_signals = list()
    for signal in ['RSI', 'RSI_Cumulative', 'kumo_breakout']:
        signal_object = Signal.objects.filter(
            source=source, transaction_currency=currency, counter_currency=counter_currency,
            signal=signal
            ).order_by('-timestamp').first()
        if signal_object:
            latest_signals.append(signal_object)

    if latest_signals:
        view += f"\n*Latest signals*"

        for signal in sorted(latest_signals, key=lambda s: s.timestamp, reverse=True):
            if signal.signal == 'RSI':
                rsi = get_rsi_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {rsi['rsi_header_emoji']} {rsi['rsi_text']}\nITF Bias: {rsi['rsi_itt_bias']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            elif signal.signal == 'RSI_Cumulative':
                rsi = get_rsi_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {rsi['rsi_header_emoji_pro']} ITF Proprietary Alert\nITF Bias: *{rsi['rsi_general_trend']}* - {rsi['rsi_itt_bias']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            elif signal.signal == 'kumo_breakout':
                kumo = get_kumo_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {kumo['ichimoku_header_emoji']} {kumo['ichimoku_text']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            else:
                continue
            view += f"{format_currency(price_new_object.price, trading_pair['counter_currency'])}\n"

    # More info
    itf_more_info_url = 'http://intelligenttrading.org/features/'
    if latest_signals:
        view += f"\n[Get more signals on ITF website]({itf_more_info_url})"
    else:
        view += f"\n[Get signals on ITF website]({itf_more_info_url})"
    #view += f" or [Ask our representative](tg://user?id=12345678)"

    # Sentiments from cryptopanic
    (title, url) = sentiment_from_cryptopanic(currency)
    if '' not in (title, url):
        view += f"\n\n\"{title}\"\n[Read on CryptoPanic]({url})"

    return view

@cache_memoize(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS) # 1 hours
def i_view(trading_pair):
    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    # Price
    price_new_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp').first()

    source = price_new_object.source
    view = f"*{currency}*\_{trading_pair['counter_currency']} *{format_currency(price_new_object.price, trading_pair['counter_currency'])}*"

    price_24h_old_object = Price.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        timestamp__lte=price_new_object.timestamp - timedelta(minutes=1440)
        ).order_by('-timestamp').first()
    try:
        percents_price_diff_24h = percents(price_new_object.price, price_24h_old_object.price)
        view += f" *{diff_symbol(percents_price_diff_24h)}*\n24hr Change: {'{:+.2f}%'.format(percents_price_diff_24h)}"
    except:
        view += "\n"

    # Volume
    volume_object = Volume.objects.filter(
        source=source, transaction_currency=currency, counter_currency=counter_currency,
        ).order_by('-timestamp').first()
    view += f"\nVolume: {format_currency(amount=volume_object.volume, currency_symbol=currency, in_satoshi=False)}"

    # Source (maybe show time in user local time not in UTC) and last update
    view += f"\n\nSource: {get_source_name(source).capitalize()}"
    view += f"\nLast update: {price_new_object.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    return view


def ta_view(trading_pair):
    counter_currency = COUNTER_CURRENCIES.index(trading_pair['counter_currency'])
    currency = trading_pair['transaction_currency']

    price_new_object = Price.objects.filter(
        transaction_currency=currency, counter_currency=counter_currency
        ).order_by('-timestamp').first()

    source = price_new_object.source

    # Signals
    latest_signals = list()
    for signal in ['RSI', 'RSI_Cumulative', 'kumo_breakout']:
        signal_object = Signal.objects.filter(
            source=source, transaction_currency=currency, counter_currency=counter_currency,
            signal=signal
            ).order_by('-timestamp').first()
        if signal_object:
            latest_signals.append(signal_object)

    if latest_signals:
        view = f"\n\n*Latest signals* for *{currency}*\_{trading_pair['counter_currency']}\n"

        for signal in sorted(latest_signals, key=lambda s: s.timestamp, reverse=True):
            if signal.signal == 'RSI':
                rsi = get_rsi_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {rsi['rsi_header_emoji']} {rsi['rsi_text']}\nITF Bias: {rsi['rsi_itt_bias']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            elif signal.signal == 'RSI_Cumulative':
                rsi = get_rsi_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {rsi['rsi_header_emoji_pro']} ITF Proprietary Alert\nITF Bias: *{rsi['rsi_general_trend']}* - {rsi['rsi_itt_bias']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            elif signal.signal == 'kumo_breakout':
                kumo = get_kumo_template(signal)
                view += f"\n *•* {format_timestamp(signal.timestamp)} {kumo['ichimoku_header_emoji']} {kumo['ichimoku_text']} ({signal.get_horizon_display().capitalize()} horizon)\n"
            else:
                continue
            view += f"{format_currency(price_new_object.price, trading_pair['counter_currency'])}\n"
    else:
        view = "Sorry, I don't have any signals for *{currency}*\_{trading_pair['counter_currency']}"
    return view

def sentiment_view(trading_pair):
    # Sentiments from cryptopanic
    (title, url) = sentiment_from_cryptopanic(trading_pair['transaction_currency'])
    view = f"Sentiment for *{trading_pair['transaction_currency']}*"

    if '' not in (title, url):
        view += f"\n\n\"{title}\"\n[Read on CryptoPanic]({url})"
    else:
        view += f"\n\n\Sorry, I don't have any sentiments for {trading_pair['transaction_currency']}"

    return view

## user commands
@restore_db_connection
def itf(bot, update, args):
    save_history(update)
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='itf')
    if trading_pair:
        view = itf_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

@restore_db_connection
def i(bot, update, args):
    save_history(update)
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='itf')
    if trading_pair:
        view = i_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

@restore_db_connection
def ta(bot, update, args):
    save_history(update)
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='ta')
    if trading_pair:
        view = ta_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

@restore_db_connection
def sentiment(bot, update, args):
    save_history(update)
    trading_pair = parse_telegram_cryptocurrency_args(args=args, update=update, command='s')
    if trading_pair:
        view = sentiment_view(trading_pair)
        update.message.reply_text(view, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    return

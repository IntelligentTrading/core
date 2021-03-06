from datetime import datetime, timedelta
import logging
import math
import re
import time

from django import db

from telegram import ParseMode

from cache_memoize import cache_memoize

from apps.indicator.models import PriceHistory
from apps.info_bot.models import InfoBotHistory

from settings import COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES, LOCAL



logger = logging.getLogger(__name__)


def parse_trading_pair_string(trading_pair_string):
    """ Convert strings like BTC/USDT, BTC_ETH, OMG/USDT, XRP
        to the {'transaction_currency': 'BTC', 'counter_currency': 'USDT'}
    """
    transaction_currency, counter_currency = None, None

    no_counter_currency_given = re.match('^[a-zA-Z0-9]{1,10}$', trading_pair_string)
    if no_counter_currency_given: # BTC
        transaction_currency = no_counter_currency_given.group()
    else: #BTC/USDT, OMG__BTC
        with_counter_currency = re.match('([a-zA-Z0-9]{1,10})[^a-zA-Z0-9]+([a-zA-Z0-9]{1,10})', trading_pair_string)
        if with_counter_currency:
            transaction_currency, counter_currency = with_counter_currency.groups()

    return {'transaction_currency': transaction_currency, 'counter_currency': counter_currency}

# FIXME this function is dublicate for taskapp.helpers get_currency_pairs. Combine them in the future
# Cache for 6 hours.
@cache_memoize(6*60*60)
def get_currency_pairs(source='all', period_in_seconds=5*60*60, counter_currency_format="text"):
    """
    Return: [('BTC', 'USDT'), ('PINK', 'ETH'), ('ETH', 'BTC'),....] for counter_currency_format="text"
    or [('BTC', 2), ('PINK', 1), ('ETH', 0),....]
    """
    get_from_time = datetime.now() - timedelta(seconds=period_in_seconds)

    if source == 'all':
        price_objects = PriceHistory.objects.values('transaction_currency', 'counter_currency').filter(timestamp__gte=get_from_time).distinct()
    else:
        price_objects = PriceHistory.objects.values('transaction_currency', 'counter_currency').filter(source=source).filter(timestamp__gte=get_from_time).distinct()
    if counter_currency_format == "index":
        currency_pairs = [(item['transaction_currency'], item['counter_currency']) for item in price_objects]
    else:
        currency_pairs = [(item['transaction_currency'], counter_currency_name(item['counter_currency'])) for item in price_objects]
    return currency_pairs

def counter_currency_name(counter_currency_index):
    "return BTC for counter_currency_index=0"
    return next((currency_name for index, currency_name in COUNTER_CURRENCY_CHOICES if index == counter_currency_index), None)

def default_counter_currency_for(transaction_currency, trading_pairs=None):
    # first USDT, BTC, ETH then others
    this_comes_first = ['USDT', 'BTC', 'ETH']
    counter_currencies = this_comes_first + list(set(COUNTER_CURRENCIES) - set(this_comes_first))
    for counter_currency in counter_currencies:
        if trading_pairs and (transaction_currency, counter_currency) in trading_pairs:
            return counter_currency
    return None

def trading_pairs_for(transaction_currency, trading_pairs=None):
    if trading_pairs:
        return [(tc, cc) for (tc, cc) in trading_pairs if tc == transaction_currency]
    return None


def natural_join(val, cnj="and"):
    if isinstance(val, list):
        return " ".join((", ".join(val[0:-1]), "%s %s" % (cnj, val[-1]))) if len(val) > 1 else val[0]
    return val

def format_timestamp(timestamp):
    return timestamp.strftime('%b %d, %H:%M')

def format_currency(amount, currency_symbol='', in_satoshi=True):
    if amount == 0:
        return f"0.00 {currency_symbol}"

    if in_satoshi: # convert from satoshis
        amount = float(amount * float(10**-8))

    common_logarithm = int(math.log10(abs(amount)))
    if common_logarithm > 3: # 12345.2212 -> 12345
        currency_norm = "{:,.0f}".format(amount)
    elif common_logarithm > 0: # 123.2212 -> 123.22
        currency_norm = "{:.2f}".format(amount)
    else: # 0.123400000 -> 0.1234
        currency_norm = "{:.6f}".format(amount).rstrip('0').rstrip('.')

    return f"{currency_norm} {currency_symbol}"


def parse_telegram_cryptocurrency_args(args, update, command):
    try:
        arg = f"{args[0]}_{args[1]}" if len(args) > 1 else args[0]
        arg = arg.upper()
    except:
        update.message.reply_text(f"Please add coin abbreviation or trading pair to command. For example: `/{command} BTC` or `/{command} ETH_USDT`", ParseMode.MARKDOWN)
        return None

    period_in_seconds = 2*60*60 if not LOCAL else 2000*60*60 # we search trading_pairs for this period back in time, more history for LOCAL env

    trading_pairs_available = get_currency_pairs(source='all', period_in_seconds=period_in_seconds, counter_currency_format="text")
    trading_pair = parse_trading_pair_string(arg)

    # wrong arg format
    if trading_pair['transaction_currency'] == trading_pair['counter_currency'] == None:
        update.message.reply_text(f"Sorry, I can't understand this coin format: `{args[0]}`. Please enter: `/{command} BTC` or `/{command} ETH_USDT`", ParseMode.MARKDOWN)
        return None
    # we don have info on this coin
    elif trading_pair['counter_currency'] is None:
        trading_pair['counter_currency'] = default_counter_currency_for(trading_pair['transaction_currency'], trading_pairs_available)
        if trading_pair['counter_currency'] is None:
            coins = set(coin for coin, _ in trading_pairs_available)
            update.message.reply_text(f"Sorry, I can't find `{trading_pair['transaction_currency']}`. Try `BTC`, `ETH`, `XRP`, `BCH` or other `{len(coins)}` coins we support.", ParseMode.MARKDOWN)
            return None
        else:
            return trading_pair
    # wrong counter currency
    elif (trading_pair['transaction_currency'], trading_pair['counter_currency']) not in trading_pairs_available:
        good_trading_pairs = []
        # try flip pair
        if (trading_pair['counter_currency'], trading_pair['transaction_currency']) in trading_pairs_available:
            good_trading_pairs.append(f"{trading_pair['counter_currency']}_{trading_pair['transaction_currency']}")

        for (tc, cc) in trading_pairs_for(trading_pair['transaction_currency'], trading_pairs_available):
            good_trading_pairs.append(f"{tc}_{cc}")

        # check other pairs for this transaction_currency
        good_trading_pairs_text = "` or `".join(good_trading_pairs)
        view = f"Sorry, I don't support this trading pair `{trading_pair['transaction_currency']}_{trading_pair['counter_currency']}`\n\n"
        if good_trading_pairs:
            view += f"Please try a different pair. For example: `{good_trading_pairs_text}`"
        update.message.reply_text(view, ParseMode.MARKDOWN)
        return None
    # all good and well
    else:
        return trading_pair

# Helpers
def save_history(update):
    try:
        InfoBotHistory.objects.create(
            update_id=update.update_id,
            group_chat_id=update.message.chat.id,
            chat_title=update.message.chat.title or "",
            user_chat_id=update.message.from_user.id,
            username=update.message.from_user.username,
            bot_command_text=update.message.text,
            language_code=update.message.from_user.language_code,
            datetime=update.message.date,
        )
        logger.debug(f">>> InfoBot history saved, update_id:{update.update_id}, chat_id:{update.message.chat.id}, user_id: {update.message.from_user.id}")
    except Exception as e:
        logging.error(f">>>Error saving history:\n{update}<<<\n{e}")

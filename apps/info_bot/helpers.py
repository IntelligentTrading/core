import logging
import math
import re
import time

from telegram import ParseMode

from cache_memoize import cache_memoize

from apps.indicator.models import Price, Volume
from settings import COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES, LOCAL

#from apps.info_bot.telegram.bot_commands.itt import currency_info



logger = logging.getLogger(__name__)

POPULAR_COINS = ('BTC', 'DASH', 'ETH', 'LTC', 'XMR', 'XRP', 'ZEC')

# def precache_currency_info_for_info_bot():
#     for currency in POPULAR_COINS:
#         logger.info('Precaching: {} for telegram info_bot'.format(currency))
#         currency_info(currency, _refresh=True) # "heat the cache up" right after we've cleared it


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
# Cache for 4 hours.
@cache_memoize(4*60*60)
def get_currency_pairs(source='all', period_in_seconds=2*60*60, counter_currency_format="text"):
    """
    Return: [('BTC', 'USDT'), ('PINK', 'ETH'), ('ETH', 'BTC'),....] for counter_currency_format="text"
    or [('BTC', 2), ('PINK', 1), ('ETH', 0),....]
    """
    get_from_time = time.time() - period_in_seconds
    if source == 'all':
        price_objects = Price.objects.values('transaction_currency', 'counter_currency').filter(timestamp__gte=get_from_time).distinct()
    else:
        price_objects = Price.objects.values('transaction_currency', 'counter_currency').filter(source=source).filter(timestamp__gte=get_from_time).distinct()
    if counter_currency_format == "index":
        currency_pairs = [(item['transaction_currency'], item['counter_currency']) for item in price_objects]
    else:
        currency_pairs = [(item['transaction_currency'], counter_currency_name(item['counter_currency'])) for item in price_objects]
    return currency_pairs

# def get_coins(currency_pairs):
#     tuple(coin for coin, _ in all)

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
        return currency_symbol + '0.00'

    if in_satoshi: # convert from satoshis
        amount = float(amount * float(10**-8))

    common_logarithm = int(math.log10(abs(amount)))
    if common_logarithm > 3: # 12345.2212 -> 12345
        currency_norm = "{:,.0f}".format(amount)
    elif common_logarithm > 0: # 123.2212 -> 123.22
        currency_norm = "{:.2f}".format(amount)
    else: # 0.123400000 -> 0.1234
        currency_norm = "{:.6f}".format(amount).rstrip('0').rstrip('.')

    return currency_symbol + currency_norm


def parse_telegram_cryptocurrency_args(args, update, command):
    try:
        arg = args[0].upper()
    except:
        update.message.reply_text(f"Please add coin abbreviation or trading pair to command. For example: `/{command} BTC` or `/{command} ETH_USDT`", ParseMode.MARKDOWN)
        return None

    period_in_seconds = 2*60*60 if not LOCAL else 2000*60*60 # we search trading_pairs for this period back in time

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
            update.message.reply_text(f"Sorry, I don't support `{trading_pair['transaction_currency']}`\n\nPlease use one of this coins:\n\n{', '.join(coins)}.\n\nOr just enter `/{command} BTC` or `/{command} ETH_USDT`", ParseMode.MARKDOWN)
            return None
        else:
            return trading_pair
    # wrong counter currency
    elif (trading_pair['transaction_currency'], trading_pair['counter_currency']) not in trading_pairs_available:
        good_trading_pairs = "` or `".join([f"{tc}_{cc}" for (tc, cc) in trading_pairs_for(trading_pair['transaction_currency'], trading_pairs_available)])
        view = f"Sorry, I don't support this trading pair `{trading_pair['transaction_currency']}_{trading_pair['counter_currency']}`\n\n"
        if good_trading_pairs:
            view += f"Please use: `{good_trading_pairs}`"
        update.message.reply_text(view, ParseMode.MARKDOWN)
        return None
    # all good and well
    else:
        return trading_pair
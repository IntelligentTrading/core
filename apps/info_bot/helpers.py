import logging
import re
import time

from cache_memoize import cache_memoize

from apps.indicator.models import Price, Volume
from settings import COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES

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
import datetime

from apps.indicator.models import PriceHistory


from settings import SOURCE_CHOICES, EXCHANGE_MARKETS
from settings import BINANCE, COUNTER_CURRENCY_CHOICES
from settings.tickers import BINANCE_WHITELIST, BLACKLISTED_COINS



def get_exchanges():
    "Return list of exchange codes for signal calculations"
    return [code for code, name in SOURCE_CHOICES if name in EXCHANGE_MARKETS]

def get_source_name(source_code):
    "return poloniex for source_code=0"
    return next((source_text for code, source_text in SOURCE_CHOICES if code == source_code), None)

def symbol_in_whitelist(source, transaction_currency, counter_currency_index, use_whitelist=True):
    if not use_whitelist: # disable whitelist and allow all symbols
        return True
    # 0 => BTC, 1=> ETH, ..."
    counter_currency_name = next((currency_name for index, currency_name in COUNTER_CURRENCY_CHOICES if index == counter_currency_index), None)
    if source == BINANCE:
        return f"{transaction_currency}/{counter_currency_name}" in BINANCE_WHITELIST
    else:
        # deny all symbols from Poloniex and Bittrex
        return False

def get_tickers(source='all', period_in_seconds=4*60*60, blacklisted_coins=None, use_whitelist=True):
    """
    set blacklisted_coins or they will loads from settings
    set use_whitelist to False if you want to disable whitelist

    set source to 'all' to return tickers with source, like [(0, 'BTC', 0), (1, 'BTC', 0), (2, 'BTC', 0),....] from all exchanges/sources
    otherwise return: [('BTC', 0), ('PINK', 0), ('ETH', 0),....]
    """
    if blacklisted_coins is None:
        blacklisted_coins = BLACKLISTED_COINS
    get_from_time = datetime.datetime.now() - datetime.timedelta(seconds=period_in_seconds)
    price_objects = PriceHistory.objects.values('source', 'transaction_currency', 'counter_currency').filter(timestamp__gte=get_from_time).distinct()
    if source == 'all':
        return [(item['source'], item['transaction_currency'], item['counter_currency'])\
            for item in price_objects\
                if symbol_in_whitelist(item['source'], item['transaction_currency'], item['counter_currency'], use_whitelist)\
                and (item['transaction_currency'] not in blacklisted_coins)]
    else:
        price_objects = price_objects.filter(source=source)
        return [(item['transaction_currency'], item['counter_currency'])\
            for item in price_objects\
                if symbol_in_whitelist(source, item['transaction_currency'], item['counter_currency'], use_whitelist)\
                and item['transaction_currency'] not in blacklisted_coins]

def quad_formatted(source, transaction_currency, counter_currency, resample_period):
    return f"{get_source_name(source)}_{transaction_currency}_{counter_currency}_{resample_period}"

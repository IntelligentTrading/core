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
        # whitelist all symbols from Poloniex and Bittrex
        return True

def get_tickers(source, period_in_seconds=4*60*60, blacklisted_coins=None, use_whitelist=True):
    """
    set blacklisted_coins or they will loads from settings
    set use_whitelist to False if you want to disable whitelist (allow all pairs)
    Return: [('BTC', 0), ('PINK', 0), ('ETH', 0),....]
    """
    if blacklisted_coins is None:
        blacklisted_coins = BLACKLISTED_COINS
    get_from_time = datetime.datetime.now() - datetime.timedelta(seconds=period_in_seconds)
    price_objects = PriceHistory.objects.values('transaction_currency', 'counter_currency').filter(source=source).filter(timestamp__gte=get_from_time).distinct()
    return [(item['transaction_currency'], item['counter_currency'])\
        for item in price_objects\
            if symbol_in_whitelist(source, item['transaction_currency'], item['counter_currency'], use_whitelist)\
            and item['transaction_currency'] not in blacklisted_coins]

def get_source_trading_pairs(back_in_time_seconds=4*60*60, blacklisted_coins=None, use_whitelist=True):
    """
    Return[(source, transaction_currency, counter_currency), (source1, transaction_currency, counter_currency) ...]
    Return: [(0, 'BTC', 0), (1, 'BTC', 0), (2, 'BTC', 0),....]
    """
    if blacklisted_coins is None:
        blacklisted_coins = BLACKLISTED_COINS
    get_from_time = datetime.datetime.now() - datetime.timedelta(seconds=back_in_time_seconds)
    price_objects = PriceHistory.objects.values('source', 'transaction_currency', 'counter_currency').filter(timestamp__gte=get_from_time).distinct()
    return [(item['source'], item['transaction_currency'], item['counter_currency'])\
        for item in price_objects\
            if symbol_in_whitelist(item['source'], item['transaction_currency'], item['counter_currency'], use_whitelist)\
            and (item['transaction_currency'] not in blacklisted_coins)]

def quad_formatted(source, transaction_currency, counter_currency, resample_period):
    return f"{get_source_name(source)}_{transaction_currency}_{counter_currency}_{resample_period}"

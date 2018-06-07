import time

from apps.indicator.models import Price

from settings import SOURCE_CHOICES, EXCHANGE_MARKETS, BLACKLISTED_COINS



def get_exchanges():
    "Return list of exchange codes for signal calculations"
    return [code for code, name in SOURCE_CHOICES if name in EXCHANGE_MARKETS]

def get_currency_pairs(source, period_in_seconds, blacklisted_coins=None):
    """
    Return: [('BTC', 0), ('PINK', 0), ('ETH', 0),....]
    """
    if blacklisted_coins is None:
        blacklisted_coins = BLACKLISTED_COINS
    get_from_time = time.time() - period_in_seconds
    price_objects = Price.objects.values('transaction_currency', 'counter_currency').filter(source=source).filter(timestamp__gte=get_from_time).distinct()
    return [(item['transaction_currency'], item['counter_currency']) for item in price_objects if item['transaction_currency'] not in blacklisted_coins]

def get_source_name(source_code):
    "return poloniex for code=0"
    return next((source_text for code, source_text in SOURCE_CHOICES if code == source_code), None)

def get_source_trading_pairs(back_in_time_seconds=2*60*60, blacklisted_coins=None):
    """
    Return[(source, transaction_currency, counter_currency), (source1, transaction_currency, counter_currency) ...]
    Return: [(0, 'BTC', 0), (1, 'BTC', 0), (2, 'BTC', 0),....]
    """
    if blacklisted_coins is None:
        blacklisted_coins = BLACKLISTED_COINS
    get_from_time = time.time() - back_in_time_seconds
    price_objects = Price.objects.values('source', 'transaction_currency', 'counter_currency').filter(timestamp__gte=get_from_time).distinct()
    return [(item['source'], item['transaction_currency'], item['counter_currency']) for item in price_objects if item['transaction_currency'] not in blacklisted_coins]

def quad_formatted(source, transaction_currency, counter_currency, resample_period):
    return f"{get_source_name(source)}_{transaction_currency}_{counter_currency}_{resample_period}"

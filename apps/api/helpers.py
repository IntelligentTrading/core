"""
Helpers and common methods for our REST API
"""

from apps.indicator.models import Price

def default_counter_currency(transaction_currency):
    if transaction_currency == 'BTC':
            counter_currency = Price.USDT
    else:
            counter_currency = Price.BTC
    return counter_currency
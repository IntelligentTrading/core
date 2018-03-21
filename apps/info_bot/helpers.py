import logging
from apps.info_bot.telegram.bot_commands.itt import currency_info



logger = logging.getLogger(__name__)

POPULAR_COINS = ('BTC', 'DASH', 'ETH', 'LTC', 'XMR', 'XRP', 'ZEC')

def precache_currency_info_for_info_bot():
    for currency in POPULAR_COINS:
        logger.info('Precaching: {} for telegram info_bot'.format(currency))
        currency_info(currency, _refresh=True) # "heat the cache up" right after we've cleared it
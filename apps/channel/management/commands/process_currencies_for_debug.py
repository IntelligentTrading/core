import logging
import time

from django.core.management.base import BaseCommand

from settings import PERIODS_LIST, SHORT, MEDIUM, LONG, POLONIEX, BINANCE, BITTREX

from taskapp.helpers import _pull_poloniex_data, _compute_and_save_indicators



logger = logging.getLogger(__name__)

#CURRENCY_PAIRS = [('BTC', 2), ('ETH', 0), ('ETH', 1)] # BTC_USDT, ETH_BTC, ETH_USDT
EXCHANGES = (POLONIEX, BINANCE) # ('poloniex', 'bittrex', 'binance')
EXCHANGES = (BINANCE,)

class Command(BaseCommand):
    help = "Process some currency pairs from some exchanges"

    # Currently we use this command for debug only
    def handle(self, *args, **options):
        logger.info("Getting ready to process currency pairs from {}".format(EXCHANGES))

        for exchange in EXCHANGES:
            _compute_and_save_indicators(source=exchange, resample_period=SHORT)


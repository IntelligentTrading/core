# @Alex Y
# Created 8.10.2017

from django.db import IntegrityError
from django.core.management.base import BaseCommand
from apps.indicator.models import Price, Volume, PriceResampled
from apps.channel.models.exchange_data import POLONIEX

from requests import get, RequestException
import logging

logger = logging.getLogger(__name__)

FETCH_URL = "https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%d&end=%d&period=300"
start_time = 1388534400  # 2014.01.01
end_time = 9999999999  # start_time + 86400*30
# TODO: Add more smart end data, may be it should be lett that oldest available crawling data...

class Command(BaseCommand):
    help = "Polls history data from Poloniex once"

    def handle(self, *args, **options):
        logger.info("Getting historical poloniex data has been started...")
        _get_usdt_historical_poloniex()
        logger.debug('> BTC and ETH prices nominated in USD have been successfully imported. ')

        _get_satosh_historical_poloniex()
        logger.debug('> the rest of currencies nominad in BTC have been successfully imported. ')


def _get_usdt_historical_poloniex():
    '''
    STEP 1:
    Get Poloniex historical data for only BTC and ETH which are nominated in USD
    :return: void
    '''

    # get BTC and ETH which are both nominated in USDT value
    USDT_PAIR_DICT = {"BTC":"USDT_BTC",
                      "ETH":"USDT_ETH"}

    # for coins nominated in USDT
    for usdt_coin, usdt_pair in USDT_PAIR_DICT.items():
        # get data from polonies
        url = FETCH_URL % (usdt_pair, start_time, end_time)
        try:
            req = get(url)
            list_of_dict = req.json()
        except RequestException:
            return 'Error collecting USDT historical data from poloniex'
        logger.debug('  =>  ' + usdt_pair + ' Data has been downloaded. Import is starting...')

        # add to price and volume DB all records for BTC and ETH
        # TODO: add assert
        for idx, rec in enumerate(list_of_dict):
            sat = int(10 ** 8) if usdt_coin == 'BTC' else int(float(rec["close"]) * 10 ** 8)
            wei = int(10 ** 8) if usdt_coin == 'ETH' else None

            try:
                Price.objects.create(
                    source=POLONIEX,
                    coin=usdt_coin,
                    timestamp=rec["date"],
                    satoshis=sat,
                    wei = wei,
                    usdt=float(rec["close"])
                )

                Volume.objects.create(
                    source=POLONIEX,
                    coin=usdt_coin,
                    timestamp=rec["date"],
                    btc_volume=float(rec["volume"])
                )
            except IntegrityError as e:
                pass
                #logger.debug("  price or volume of coin/time already exists, adding skipped...")


            if idx % 20000 == 0:
                logger.debug('  ... records imported: ' + str(idx))



def _get_satosh_historical_poloniex():
    '''
    STEP 2:
    gets Poloniex historical prices in satoshies(BTC) for all currencies except BTC itself and ETH
    the latter two are nominated in USDT
    then save those historical prices in Price table
    if runing twice, no duplicates are created (coin/timestamp is a unique combination)
    :return: void
    '''

    # get list of all available currencies_to_BTC pairs with their respective names
    # curr_pair_dict = {"ETH": "BTC_ETH" ..... }
    req = get("https://poloniex.com/public?command=return24hVolume").json()
    curr_pair_dict = {}    # = {"ETH": "BTC_ETH" ..... }
    for currency_pair in req:
        if currency_pair.split('_')[0] == "BTC":
            coin = currency_pair.split('_')[1]
            curr_pair_dict[coin] = currency_pair

    # get historical data for all curencies nominated in BTC
    for coin_name, btc_pair in curr_pair_dict.items():
        # get data from polonies for current pair
        url = FETCH_URL % (btc_pair, start_time, end_time)
        try:
            req = get(url)
            list_of_dict = req.json()
        except RequestException:
            return 'Error collecting BTC_XXX historical data from poloniex'
        logger.debug('  =>  ' + btc_pair + ' Data has been downloaded. Import is starting...')

        # add to price and volume DB all records for BTC and ETH
        # TODO: add assert
        for idx, rec in enumerate(list_of_dict):
            sat = int(float(rec["close"]) * 10 ** 8)

            try:
                Price.objects.create(
                    source=POLONIEX,
                    coin=coin_name,
                    timestamp=rec["date"],
                    satoshis=sat
                )

                Volume.objects.create(
                    source=POLONIEX,
                    coin=coin_name,
                    timestamp=rec["date"],
                    btc_volume=float(rec["volume"])
                )
            except IntegrityError as e:
                pass
                # logger.debug("  price or volume of coin/time already exists, adding skipped...")

            if idx % 20000 == 0:
                logger.debug('  ... records imported and saved: ' + str(idx))

import json
import logging
import schedule
import time
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)
        # @Alex
        schedule.every(1).minutes.do(_resample_and_sma, {'period':5} )

        keep_going=True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Poloniex Trawl shut down.")
                keep_going = False


def pull_poloniex_data():
    try:
        logger.info("pulling Poloniex data...")
        req = get('https://poloniex.com/public?command=returnTicker')

        data = req.json()
        timestamp = time.time()

        poloniex_data_point = ExchangeData.objects.create(
            source=POLONIEX,
            data=json.dumps(data),
            timestamp=timestamp
        )
        logger.info("Saving Poloniex price, volume data...")
        _save_prices_and_volumes(data, timestamp)

    except RequestException:
        return 'Error to collect data from Poloniex'


def _save_prices_and_volumes(data, timestamp):
    try:
        usdt_btc = data.pop("USDT_BTC")

        Price.objects.create(
            source=POLONIEX,
            coin="BTC",
            satoshis=int(10 ** 8),
            usdt=float(usdt_btc['last']),
            timestamp=timestamp
        )

        Volume.objects.create(
            source=POLONIEX,
            coin="BTC",
            btc_volume=float(usdt_btc['baseVolume']),
            timestamp=timestamp
        )

    except KeyError:
        logger.debug("missing BTC in Poloniex data")

    try:
        usdt_eth = data.pop("USDT_ETH")
        btc_eth = data.pop("BTC_ETH")

        Price.objects.create(
            source=POLONIEX,
            coin="ETH",
            satoshis=int(float(btc_eth['last']) * 10 ** 8),
            wei=int(10 ** 8),
            usdt=float(usdt_eth['last']),
            timestamp=timestamp
        )

        Volume.objects.create(
            source=POLONIEX,
            coin="ETH",
            btc_volume=float(btc_eth['baseVolume']),
            timestamp=timestamp
        )

    except KeyError:
        logger.debug("missing ETH in Poloniex price data")

    for currency_pair in data:
        if currency_pair.split('_')[0] == "BTC":
            try:
                Price.objects.create(
                    source=POLONIEX,
                    coin=currency_pair.split('_')[1],
                    satoshis=int(float(data[currency_pair]['last']) * 10 ** 8),
                    timestamp=timestamp
                )
                Volume.objects.create(
                    source=POLONIEX,
                    coin=currency_pair.split('_')[1],
                    btc_volume=float(data[currency_pair]['baseVolume']),
                    timestamp = timestamp
                )
            except Exception as e:
                logger.debug(str(e))

    logger.debug("Saved Poloniex price and volume data")

# @Alex
def _resample_and_sma(period):
    logger.debug("======== START resampling and SMA ========= ")

    # get all records back in time ( 5 min)
    period_records = Price.objects.filter(timestamp__gte=datetime.now()-timedelta(minutes=10)) # must be period

    # ETC: calculate average values for the records 5 min back in time
    eth = list(period_records.filter(coin="ETH").values('timestamp','satoshis').order_by('-timestamp'))
    prices = np.array([ rec['satoshis'] for rec in eth])
    times = np.array([ rec['timestamp'] for rec in eth])
    period_val = prices.mean()
    period_ts = times.max()
    logger.debug('========> Time:' + str(period_ts) + 'Average value:::'  + str(period_val))

    # get history data from new table

    # calculate SMA with ta-lib stream

    # add new record to a new table price_resampled_5

    logger.debug("Price is resampled and SMA calculated for all currencies")

    pass

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
from apps.indicator.models import Price, Volume, PriceResampled

logger = logging.getLogger(__name__)

# @Alex
coins_list = ["ETH", "XRP", "LTC", "DASH", "NEO", "XMR", "OMG"]
periods_list = [15, 60, 360]
#horizons = {15:"short", 60:"medium", 360: "long"}
time_speed = 1      #set to 1 for production, 10 for fast debugging


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)

        # @Alex
        #schedule.every(5).minutes.do(_resample_and_sma, {'period':5} )
        schedule.every(15/time_speed).minutes.do(_resample_then_metrics, {'period': 15})
        schedule.every(60/time_speed).minutes.do(_resample_then_metrics, {'period': 60})
        schedule.every(360/time_speed).minutes.do(_resample_then_metrics, {'period': 360})

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
def _resample_then_metrics(period_par):
    '''
    Shall be ran every 15, 60, 360 min from the scheduler
    First: resampling - create a new price dataset with differend sampling frequency, put 15 minutes into one datapoint (bin)
    Second: calculate additional metrics SMA 50 and SMA 200 and put them into the same table
    Finally: run signal detection and emit a signal if nessesary

    :param period_par: a dictionary with the only key period_par['period'] which is a bin size(period) one of 15,60,360
    :return: void
    '''

    # TODO: need to be refactored... splitted into several methods or classes

    period = period_par['period']
    logger.debug("======== Resampling with Period: " + str(period))

    # get all records back in time ( 5 min)
    period_records = Price.objects.filter(timestamp__gte=datetime.now()-timedelta(minutes=period))

    for coin in coins_list:
        #logger.debug('  COIN: '+ str(coin))
        # calculate average values for the records 5 min back in time
        coin_price_list = list(period_records.filter(coin=coin).values('timestamp','satoshis').order_by('-timestamp'))

        # skip the currency if there is no data about this currency
        if not coin_price_list: continue

        prices = np.array([ rec['satoshis'] for rec in coin_price_list])
        times = np.array([ rec['timestamp'] for rec in coin_price_list])
        period_mean = prices.mean()
        period_min = prices.min()
        period_max = prices.max()
        period_ts = times.max()

        # save new resampled point in the Table
        price_resampled_object = PriceResampled.objects.create(
            source=POLONIEX,
            coin=coin,
            timestamp=period_ts,
            period = period,
            mean_price_satoshis=period_mean,
            min_price_satoshis=period_min,
            max_price_satoshis=period_max
        )
        #logger.debug("  Price is resampled")

        # get last 250 historical point which is enough to calculate any SMA,EMA etc
        logger.debug("...SMA, EMA")
        price_resampled_object.calc_SMA()
        price_resampled_object.save()

        price_resampled_object.calc_EMA()
        price_resampled_object.save()

        logger.debug("...check signals")
        price_resampled_object.check_signal()


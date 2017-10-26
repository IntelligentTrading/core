import json
import logging
import schedule
import time
import pandas as pd
import numpy as np
import talib.stream as tas

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume, PriceResampled

logger = logging.getLogger(__name__)

# @Alex
coins_list = ["ETH", "XRP", "LTC", "DASH", "NEO", "XMR", "OMG"]


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)

        # @Alex
        #schedule.every(5).minutes.do(_resample_and_sma, {'period':5} )
        schedule.every(15).minutes.do(_resample_and_sma, {'period': 15})
        schedule.every(60).minutes.do(_resample_and_sma, {'period': 60})
        schedule.every(360).minutes.do(_resample_and_sma, {'period': 360})

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
def _resample_and_sma(period_par):
    period = period_par['period']

    logger.debug("============ Resampling and SMA, Resampling Period: " + str(period))

    # get all records back in time ( 5 min)
    period_records = Price.objects.filter(timestamp__gte=datetime.now()-timedelta(minutes=period))

    for coin in coins_list:
        logger.debug('  COIN: '+str(coin))
        # calculate average values for the records 5 min back in time
        coin_price_list = list(period_records.filter(coin=coin).values('timestamp','satoshis').order_by('-timestamp'))

        # skip the currency if there is no information about this currency
        if not coin_price_list:
            logger.debug('   ------> Currency skipped')
            continue

        prices = np.array([ rec['satoshis'] for rec in coin_price_list])
        times = np.array([ rec['timestamp'] for rec in coin_price_list])
        period_mean = prices.mean()
        period_min = prices.min()
        period_max = prices.max()
        period_ts = times.max()
        logger.debug('    Time:' + str(period_ts) + ' || ' + str(coin) + ' Average value:::'  + str(period_mean))

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
        logger.debug(' Resampled data has been saved')

        # get resampled data(period=15, coin="ETH")  for SMA calculation
        # TODO: need to limit data back in time.. otherwise in a year it might take too much time in memory...
        raw_data = list(PriceResampled.objects.filter(period=period, coin=coin).values('mean_price_satoshis'))

        if raw_data:  # if we have at least on bin (to avoid SMA error)
            # calculate SMA and save it in the same record
            price_ts = np.array([ rec['mean_price_satoshis'] for rec in raw_data])
            SMA50 = tas.SMA(price_ts.astype(float), timeperiod=50)
            SMA200 = tas.SMA(price_ts.astype(float), timeperiod=200)

            if not np.isnan(SMA50): price_resampled_object.SMA50_satoshis = SMA50
            if not np.isnan(SMA200): price_resampled_object.SMA200_satoshis = SMA200
            price_resampled_object.save()

    logger.debug("=========> DONE. Price is resampled and SMA calculated for all currencies")

    # emit a buy/sell signal to print for now
    #_isEmitSignal()


# check if we need to emit signal
def _isEmitSignal():
    logger.debug("EMIT started =========>")
    # for short, medium and long period trading
    periods_list = [15, 60, 360]
    epsilon = 4.5

    for period in periods_list:
        for coin in coins_list:
            logger.debug('  COIN: ' + str(coin))
            # get the last
            last_row = list(PriceResampled.objects.filter(period=period, coin=coin).order_by('-timestamp').values('mean_price_satoshis','SMA50_satoshis','SMA200_satoshis'))[0]
            # skip the currency if there is no information about this currency
            if not last_row:
                logger.debug('----------> EMIT skipped')
                continue

            price = last_row['mean_price_satoshis']
            SMA50 = last_row['SMA50_satoshis']
            SMA200 = last_row['SMA200_satoshis']

            ind_A = price - SMA50
            ind_B = price - SMA200
            ind_C = SMA50 - SMA200

            sgCross_price_SMA_short = np.sign(ind_A) if ind_A < epsilon else 0
            sgCross_price_SMA_middle = np.sign(ind_B) if ind_B < epsilon else 0
            sgCross_price_SMA_long = np.sign(ind_C) if ind_C < epsilon else 0

            logger.info('======> Cross_price_SMA_short SIGNAL::' + str(sgCross_price_SMA_short))
            logger.info('======> Cross_price_SMA_middle SIGNAL::' + str(sgCross_price_SMA_middle))
            logger.info('======> Cross_price_SMA_long SIGNAL::' + str(sgCross_price_SMA_long))


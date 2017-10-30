import json
import logging
import schedule
import time
import pandas as pd
import numpy as np
# import talib.stream as tas

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume, PriceResampled
from apps.indicator.telegram_alert import TelegramAlert

logger = logging.getLogger(__name__)

# @Alex
coins_list = ["ETH", "XRP", "LTC", "DASH", "NEO", "XMR", "OMG"]
periods_list = [15, 60, 360]
horizons = {15:"short", 60:"medium", 360: "long"}
time_speed = 1      #set to 1 for production, 15 for fast debugging


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)

        # @Alex
        #schedule.every(5).minutes.do(_resample_and_sma, {'period':5} )
        schedule.every(15/time_speed).minutes.do(_resample_and_sma, {'period': 15})
        schedule.every(60/time_speed).minutes.do(_resample_and_sma, {'period': 60})
        schedule.every(360/time_speed).minutes.do(_resample_and_sma, {'period': 360})

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
    logger.debug("============ Resampling and SMA, Resampling Period: " + str(period))

    # get all records back in time ( 5 min)
    period_records = Price.objects.filter(timestamp__gte=datetime.now()-timedelta(minutes=period))

    for coin in coins_list:
        #logger.debug('  COIN: '+str(coin))
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

        # get resampled data(period=15, coin="ETH")  for SMA calculation
        # TODO: need to limit data back in time.. otherwise in a year it might take too much time in memory...
        raw_data = list(PriceResampled.objects.filter(period=period, coin=coin).values('mean_price_satoshis'))

        if raw_data:  # if we have at least on bin (to avoid SMA error)
            # calculate SMA and save it in the same record
            price_ts = np.array([ rec['mean_price_satoshis'] for rec in raw_data])
            # SMA50 = tas.SMA(price_ts.astype(float), timeperiod=50/time_speed)
            # SMA200 = tas.SMA(price_ts.astype(float), timeperiod=200/time_speed)

            # if not np.isnan(SMA50): price_resampled_object.SMA50_satoshis = SMA50
            # if not np.isnan(SMA200): price_resampled_object.SMA200_satoshis = SMA200
            price_resampled_object.save()

    logger.debug("=========> DONE. Price is resampled and SMA calculated for all currencies")

    # check for a buy/sell signal to print for now
    _check_signal()


# check if we need to emit signal
def _check_signal():
    '''
    Shall be ran exactly after new SMA values have been calculated
    emit a signal to buy/sell if one of the indicators A,B,C changes its sign since the last calculation
    :return: void
    '''

    # TODO: Need to be refactored
    # for all periods and coins separatelly
    for period in periods_list:
        for coin in coins_list:
            #logger.debug('  COIN: ' + str(coin))

            # get the last
            last_two_rows = list(PriceResampled.objects.filter(period=period, coin=coin).order_by('-timestamp').values('mean_price_satoshis','SMA50_satoshis','SMA200_satoshis'))[0:2]
            # skip the currency if there is no information about this currency
            if not last_two_rows:
                #logger.debug('----------> EMIT skipped')
                continue

            prices = np.array([ row['mean_price_satoshis'] for row in last_two_rows])
            SMA50s = np.array([ row['SMA50_satoshis'] for row in last_two_rows])
            SMA200s = np.array([ row['SMA200_satoshis'] for row in last_two_rows])

            # check for ind_A signal
            if all(prices != None) and all(SMA50s != None):
                ind_A = np.sign(prices - SMA50s)
                if ind_A[0] == 0: print(prices, SMA50s)
                if np.sum(ind_A) == 0 and any(ind_A) != 0 :  # emit a signal if indicator changes its sign
                    print(ind_A)
                    alert_A = TelegramAlert(
                        coin=coin,
                        signal="SMA",
                        trend=int(ind_A[0]),
                        horizon=horizons[period],
                        strength_value=int(1),
                        strength_max=int(3)

                    )
                    alert_A.print()
                    alert_A.send()

            if all(prices != None) and all(SMA200s != None):
                ind_B = np.sign(prices - SMA200s)
                if ind_B[0] == 0: print(prices, SMA200s)
                if np.sum(ind_B) == 0 and any(ind_B) != 0:
                    print(ind_B)
                    alert_B = TelegramAlert(
                        coin=coin,
                        signal="SMA",
                        trend=int(ind_B[0]),
                        horizon=horizons[period],
                        strength_value=int(2),
                        strength_max=int(3)

                    )
                    alert_B.print()
                    alert_B.send()

            if all(SMA200s != None) and all(SMA50s != None):
                ind_C = np.sign(SMA50s - SMA200s)
                if ind_C[0] == 0: print(prices, SMA200s)

                if np.sum(ind_C) == 0 and any(ind_C) != 0:
                    print(ind_C)
                    alert_C = TelegramAlert(
                        coin=coin,
                        signal="SMA",
                        trend=int(ind_C[0]),
                        horizon=horizons[period],
                        strength_value=int(3),
                        strength_max=int(3)

                    )
                    alert_C.print()
                    alert_C.send()


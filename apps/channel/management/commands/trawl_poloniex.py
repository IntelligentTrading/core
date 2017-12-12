import json
import logging
import schedule
import time
import numpy as np
import itertools

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume, PriceResampled
from apps.indicator.models.price import get_currency_value_from_string

from settings import time_speed  # 1 / 10
from settings import COINS_LIST_TO_GENERATE_SIGNALS
from settings import PERIODS_LIST  # PERIODS_LIST = [15, 60, 360]

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        schedule.every(1).minutes.do(pull_poloniex_data)

        # @Alex
        # run resampling in 15,60,360 bins and calculate indicator values
        schedule.every(PERIODS_LIST[0] / time_speed).minutes.do(_resample_then_metrics, {'period': PERIODS_LIST[0]})
        schedule.every(PERIODS_LIST[1] / time_speed).minutes.do(_resample_then_metrics, {'period': PERIODS_LIST[1]})
        schedule.every(PERIODS_LIST[2] / time_speed).minutes.do(_resample_then_metrics, {'period': PERIODS_LIST[2]})

        keep_going = True
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
    for currency_pair in data:
        try:
            counter_currency_string = currency_pair.split('_')[0]
            counter_currency = get_currency_value_from_string(counter_currency_string)
            assert counter_currency >= 0
            transaction_currency_string = currency_pair.split('_')[1]
            assert len(transaction_currency_string) > 1 and len(transaction_currency_string) <= 6

            Price.objects.create(
                source=POLONIEX,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                price=int(float(data[currency_pair]['last']) * 10 ** 8),
                timestamp=timestamp
            )

            Volume.objects.create(
                source=POLONIEX,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                volume=float(data[currency_pair]['baseVolume']),
                timestamp=timestamp
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
    logger.debug(" ============== Resampling with Period: " + str(period) + " ====")

    # get all records back in [period] time ( 15min, 60min, 360min)
    period_records = Price.objects.filter(timestamp__gte=datetime.now() - timedelta(minutes=period))

    # for all transaction_currencys destined to be resamples
    # COINS_LIST = ["ETH", "XRP", "LTC", "DASH", "NEO", "XMR", "OMG"]
    BASE_COIN_TO_FILL = [Price.BTC, Price.USDT]

    # iterate over all pairs [('ETH', 0), ('ETH', 1), ('XRP', 0), ('XRP', 1) ...
    for transaction_currency, counter_currency in itertools.product(COINS_LIST_TO_GENERATE_SIGNALS, BASE_COIN_TO_FILL):
        logger.debug(' ======= resampling: checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(counter_currency))

        # get all price records back in time (according to period)
        transaction_currency_price_list = list(
            period_records.filter(transaction_currency=transaction_currency, counter_currency=counter_currency).values('timestamp', 'price').order_by('-timestamp'))

        # skip the currency if there is no given price
        if not transaction_currency_price_list:
            logger.debug(' ======= skipping, no price information')
            continue

        # todo can i do better?
        # get values from django structure
        prices = np.array([rec['price'] for rec in transaction_currency_price_list])
        times = np.array([rec['timestamp'] for rec in transaction_currency_price_list])

        ### resample price data, i.e. generate one time point for each 15 min
        period_variance = prices.var()
        period_mean = int(prices.mean())  # we need it all int becasue we decided to * 10^8
        period_min = int(prices.min())
        period_max = int(prices.max())
        period_closing = int(prices[-1])
        period_ts = times.max()

        # create resampled object
        price_resampled_object = PriceResampled.objects.create(
            source=POLONIEX,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
            timestamp=period_ts,
            period=period,
            price_variance=period_variance,
            mean_price=period_mean,
            closing_price=period_closing,
            min_price=period_min,
            max_price=period_max

        )

        # calculate additional indicators (sma, ema etc)
        logger.debug("   calculate indicators for [ " + str(transaction_currency) + " ], price in :" + str(counter_currency) )

        try:
            price_resampled_object.calc_SMA()
            price_resampled_object.save()
            logger.debug("   ...SMA calculations done and saved.")
        except Exception as e:
            logger.debug('---> SMA calculation error: ' + str(e))

        try:
            price_resampled_object.calc_EMA()
            price_resampled_object.save()
            logger.debug("   ...EMA calculations done and saved.")
        except Exception as e:
            logger.debug('---> EMA calcultion error: ' +  str(e))

        try:
            price_resampled_object.calc_RS()
            price_resampled_object.save()
            logger.debug("   ...RS calculations done and saved.")
        except Exception as e:
            logger.debug(str(e))

        ### check and generate possible signals
        # todo: move the check_signal logic from price_resampled to a static method of Signal
        try:
            logger.debug("   ...check cross over signals to emit")
            price_resampled_object.check_cross_over_signal()
        except Exception as e:
            logging.debug(" --> error checking cross over signals: " + str(e))

        # check RSI if period more then 15 (Vinnie told that it makes not sense
        # to run RSI for 15 min period, so we calculate it only for 60, 360
        if period >= 15:  # change to 60 in production
            try:
                logger.debug("   ...check RSI signal to emit")
                price_resampled_object.check_rsi_signal()
            except Exception as e:
                logging.debug(" --> error checking rsi signals: " + str(e))

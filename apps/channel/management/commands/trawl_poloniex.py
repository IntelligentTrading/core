import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException
from datetime import timedelta, datetime
import numpy as np

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume
from apps.indicator.models.price import get_currency_value_from_string
from apps.indicator.models.price_resampl import get_n_last_resampl_df, get_first_resampled_time

from settings import time_speed  # 1 / 10
from settings import USDT_COINS, BTC_COINS
from settings import PERIODS_LIST

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")

        schedule.every(1/time_speed).minutes.do(_pull_poloniex_data)

        # @Alex
        # run resampling for all periods and calculate indicator values
        # TODO synchronize the start with beginning of hours / days / etc
        for hor_period in PERIODS_LIST:
            schedule.every(hor_period / time_speed).minutes.do(
                _compute_and_save_indicators,
                {'period': hor_period}
            )


        keep_going = True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Poloniex Trawl shut down.")
                keep_going = False


def _pull_poloniex_data():
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


def _compute_and_save_indicators(resample_period_par):
    from apps.indicator.models.price_resampl import PriceResampl
    from apps.indicator.models.sma import Sma
    from apps.indicator.models.rsi import Rsi
    from apps.indicator.models.events_elementary import EventsElementary
    from apps.indicator.models.events_logical import EventsLogical

    timestamp = time.time()
    resample_period = resample_period_par['period']

    logger.debug(" ################# Resampling with Period: " + str(resample_period) + " #######################")

    pairs_to_iterate = [(itm,Price.USDT) for itm in USDT_COINS] + [(itm,Price.BTC) for itm in BTC_COINS]
    for transaction_currency, counter_currency in pairs_to_iterate:

        logger.debug('   ======== checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(counter_currency))

        # create a dictionary of parameters to improve readability
        indicator_params_dict = {
            'timestamp' : timestamp,
            'source' : POLONIEX,
            'transaction_currency' : transaction_currency,
            'counter_currency' : counter_currency,
            'resample_period' : resample_period
        }
        ################# BACK CALCULATION (need only once when run first time)
        # first time run only for low period
        if resample_period == 60:
            # calculate at least 200 records back in time to give sma enough information
            BACK_REC = 210
            BACK_TIME = timestamp - BACK_REC * resample_period * 60  # shall be in sec

            last_time_computed = get_first_resampled_time(POLONIEX, transaction_currency, counter_currency, resample_period)
            records_to_compute = int((last_time_computed-BACK_TIME)/(resample_period * 60))

            if records_to_compute >= 0:
                logger.debug("  ... calculate resampl back in time, needed records: " + str(records_to_compute))
                for idx in range(1, records_to_compute):
                    time_point_back = last_time_computed - idx * (resample_period * 60)
                    indicator_params_dict['timestamp'] = time_point_back
                    try:
                        resample_object = PriceResampl.objects.create(**indicator_params_dict)
                        status = resample_object.compute()
                        if status or (idx == records_to_compute-1) : # leave the last empty record
                            resample_object.save()
                        else:
                            resample_object.delete()  # delete record if no price was added
                    except Exception as e:
                        logger.error(" -> Back RESAMPLE EXCEPTION: " + str(e))
                logger.debug("... resample back  - DONE.")
            else:
                logger.debug("   ... No back calculation needed")

            # set time back to a current time
            indicator_params_dict['timestamp'] = timestamp

        ################# Can be commented after first time run

        # calculate and save resampling price
        # todo - prevent adding an empty record if no value was computed (static method below)
        try:
            resample_object = PriceResampl.objects.create(**indicator_params_dict)
            resample_object.compute()
            resample_object.save()
        except Exception as e:
            logger.error(" -> RESAMPLE EXCEPTION: " + str(e))

        # calculate and save simple indicators
        indicators_list = [Sma, Rsi]
        for ind in indicators_list:
            try:
                ind.compute_all(ind, **indicator_params_dict)
            except Exception as e:
                logger.error(str(ind) + " Indicator Exception: " + str(e))

        # check for events and save if any
        # todo: make sure EventsElementary runs first

        events_list = [EventsElementary, EventsLogical]
        for event in events_list:
            try:
                event.check_events(event, **indicator_params_dict)
            except Exception as e:
                logger.error("Event Exception: " + str(e))

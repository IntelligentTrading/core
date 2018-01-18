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

    BASE_COIN_TO_FILL = [Price.BTC, Price.USDT]
    logger.debug(" ============== Resampling with Period: " + str(resample_period) + " ====")

    for transaction_currency, counter_currency in itertools.product(COINS_LIST_TO_GENERATE_SIGNALS, BASE_COIN_TO_FILL):
        # todo get constants in a better way
        if (transaction_currency == 'BTC') & (counter_currency == 0):
            continue

        logger.debug('          checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(counter_currency))

        # create a dictionary of parameters to improve readability
        indicator_params_dict = {
            'timestamp' : timestamp,
            'source' : POLONIEX,
            'transaction_currency' : transaction_currency,
            'counter_currency' : counter_currency,
            'resample_period' : resample_period
        }

        # calculate and save resampling price
        # todo - prevent adding an empty record if no value was computed (static method below)
        try:
            resample_object = PriceResampl.objects.create(**indicator_params_dict)
            resample_object.compute()
            resample_object.save()
        except Exception as e:
            logger.error("RESAMPLE EXCEPTION: " + str(e))

        # calculate and save simple indicators
        indicators_list = [Sma, Rsi]
        for ind in indicators_list:
            try:
                ind.compute_all(ind, **indicator_params_dict)
            except Exception as e:
                logger.error("Indicator Exception: " + str(e))

        # check for events and save if any
        # todo: make sure EventsElementary runs first

        events_list = [EventsElementary, EventsLogical]
        for event in events_list:
            try:
                event.check_events(event, **indicator_params_dict)
            except Exception as e:
                logger.error("Event Exception: " + str(e))



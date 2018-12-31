import logging
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from apps.TA import PRICE_INDEXES
from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
from apps.common.utilities.multithreading import start_new_thread, multithread_this_shit
from apps.TA.storages.utils import missing_data
from settings.redis_db import database

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Redis Data gaps filler'

    def add_arguments(self, parser):
        parser.add_argument('arg', nargs='?', default='force_fill_gaps', type=str)

    def handle(self, *args, **options):
        logger.info("Starting data gaps restoration...")

        arg = options['arg']

        # See if the worker missed generating PV values
        # refill_pv_storages()

        fill_data_gaps(SQL_fill=True, force_fill=False)
        # fill_data_gaps(SQL_fill=True, force_fill=(arg=='force_fill_gaps'))
        fill_data_gaps(SQL_fill=False, force_fill=True)


def fill_data_gaps(SQL_fill=False, force_fill=False):
    method_params = []

    for ticker in ["BTC_USDT", ]:  # ["*_USDT", "*_BTC"]:
        for exchange in ["binance", ]:  # ["binance", "poloniex", "bittrex"]:
            for index in ['close_volume', 'open_price', 'high_price', 'low_price', 'close_price']:

                for key in database.keys(f"{ticker}*{exchange}*PriceStorage*{index}*"):
                    [ticker, exchange, storage_class, index] = key.decode("utf-8").split(":")

                    ugly_tuple = (ticker, exchange, index, bool(SQL_fill))
                    method_params.append(ugly_tuple)

    logger.info(f"{len(method_params)} tickers ready to fill gaps")

    results = multithread_this_shit(condensed_fill_redis_gaps, method_params)
    missing_scores_count = sum([len(result) for result in results])

    logger.warning(f"{missing_scores_count} scores could not be recovered and are still missing.")

    # if SQL_fill:
    #     results = multithread_this_shit(condensed_fill_SQL_gaps, method_params)
    #     missing_scores_count = sum([len(result) for result in results])
    #     logger.warning(f"{missing_scores_count} scores could not be recovered and are still missing.")

    if force_fill:
        logger.warning("STARTING FORCE FILL OF THESE VALUES...")
        logger.warning("!! THERE'S NO GOING BACK FROM HERE. DATA MAY WILL BE PERMAMENTLY CORRUPTED !!")
        for missing_scores in results:
            missing_data.force_plug_pv_storage_data_gaps(ticker, exchange, index, missing_scores)


def refill_pv_storages():
    from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
    from apps.TA.storages.utils.pv_resampling import generate_pv_storages
    from apps.TA.storages.utils.memory_cleaner import clear_pv_history_values

    start_score = int(TimeseriesStorage.score_from_timestamp(datetime(2018, 1, 1).timestamp()))
    end_score = int(TimeseriesStorage.score_from_timestamp(datetime.now().timestamp()))  # 206836 is Dec 20

    tei_processed = {}

    for key in database.keys("BTC_USDT*PriceVolumeHistoryStorage*"):
        logger.info("running pv refill for " + str(key))
        [ticker, exchange, object_class, index] = key.decode("utf-8").split(":")

        for score in range(start_score, end_score):
            generate_pv_storages(ticker, exchange, index, score)

            if not (ticker + exchange) in tei_processed:
                tei_processed[ticker + exchange] = []  # initialize with 0 indexes

            tei_processed[ticker + exchange].append(index)  # add indexes
            if len(tei_processed[ticker + exchange]) >= 5:  # vol + price hloc
                clear_pv_history_values(ticker, exchange, score)


def condensed_fill_redis_gaps(ugly_tuple):
    (ticker, exchange, index, back_to_the_backlog) = ugly_tuple
    return missing_data.find_pv_storage_data_gaps(ticker, exchange, index, back_to_the_backlog=False)


def condensed_fill_SQL_gaps(ugly_tuple):
    (ticker, exchange, index, back_to_the_backlog) = ugly_tuple
    return missing_data.find_pv_storage_data_gaps(ticker, exchange, index, back_to_the_backlog=True)

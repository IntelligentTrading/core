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
        parser.add_argument('arg', nargs='?', default='force_fill_SQL', type=str)

    def handle(self, *args, **options):
        logger.info("Starting data gaps restoration...")

        arg = options['arg']

        # fill_data_gaps(SQL_fill=False, force_fill=False)
        #
        # from apps.TA.management.commands.TA_restore import restore_db_to_redis
        # for month in range(4,11):
        #     restore_db_to_redis(
        #         datetime(2018, month, 1),
        #         datetime(2018, month+1, 1),
        #     )

        # First, fill missing data from SQL
        fill_data_gaps(SQL_fill=True, force_fill=False)
        # Second, try to fix yourself inside Redis only
        fill_data_gaps(SQL_fill=False, force_fill=False)
        # Third, final pass, pulling from SQL and forcing values if demanded in arg
        fill_data_gaps(SQL_fill=True, force_fill=(arg=='force_fill_gaps'))


def fill_data_gaps(SQL_fill = False, force_fill=False):

    method_params = []

    for ticker in ["BTC_USDT",]:  # ["*_USDT", "*_BTC"]:
        for exchange in ["binance", ]:  # ["binance", "poloniex", "bittrex"]:
            for index in ['close_price', 'open_price', 'high_price', 'low_price', 'close_volume']:

                for key in database.keys(f"{ticker}*{exchange}*PriceStorage*{index}*"):
                    [ticker, exchange, storage_class, index] = key.decode("utf-8").split(":")

                    ugly_tuple = (ticker, exchange, index, bool(SQL_fill))
                    method_params.append(ugly_tuple)

    logger.info(f"{len(method_params)} tickers ready to fill gaps")

    results = multithread_this_shit(condensed_fill_redis_gaps, method_params)

    missing_scores_count = sum([len(result) for result in results])
    logger.warning(f"{missing_scores_count} scores could not be recovered and are still missing.")

    if SQL_fill:
        results = multithread_this_shit(condensed_fill_SQL_gaps, method_params)
        missing_scores_count = sum([len(result) for result in results])
        logger.warning(f"{missing_scores_count} scores could not be recovered and are still missing.")

    if force_fill:
        logger.warning("STARTING FORCE FILL OF THESE VALUES...")
        logger.warning("!! THERE'S NO GOING BACK FROM HERE. DATA MAY WILL BE PERMAMENTLY CORRUPTED !!")
        for missing_scores in results:
            missing_data.force_plug_pv_storage_data_gaps(ticker, exchange, index, missing_scores)


def condensed_fill_redis_gaps(ugly_tuple):
    (ticker, exchange, index, back_to_the_backlog) = ugly_tuple
    return missing_data.find_pv_storage_data_gaps(ticker, exchange, index, back_to_the_backlog=False)

def condensed_fill_SQL_gaps(ugly_tuple):
    (ticker, exchange, index, back_to_the_backlog) = ugly_tuple
    return missing_data.find_pv_storage_data_gaps(ticker, exchange, index, back_to_the_backlog=True)

### OLD todo: rewrite to run much much faster, batching redis queries ###

### RESAMPLE PRICES TO 5 MIN PRICE STORAGE RECORDS ###
@start_new_thread
def price_history_to_price_storage(ticker_exchanges, start_score=None, end_score=None):
    from apps.TA.storages.utils.pv_resampling import generate_pv_storages
    from apps.TA.storages.utils.memory_cleaner import clear_pv_history_values
    from apps.TA.storages.data.pv_history import default_price_indexes

    if not start_score:
        # start_score = 0  # this is jan 1 2017
        start_score = int(
            (datetime(2018, 9, 1).timestamp() - datetime(2017, 1, 1).timestamp()) / 300
        )  # this is Sep 1 2018
    processing_score = start_score

    if not end_score:
        end_score = TimeseriesStorage.score_from_timestamp((datetime.today() - timedelta(hours=2)).timestamp())

    logger.debug(f"STARTING price resampling for scores {start_score} to {end_score}")

    while processing_score < end_score:
        processing_score += 1

        for ticker, exchange in ticker_exchanges:
            for index in default_price_indexes:
                if generate_pv_storages(ticker, exchange, index, processing_score):
                    if index == "close_price":
                        clear_pv_history_values(ticker, exchange, processing_score)

    logger.debug(f"FINISHED price resampling for scores {start_score} to {end_score}")
    # returns nothing - can be threaded with collection of results
### END RESAMPLE FOR PRICE STORAGE RECORDS ###

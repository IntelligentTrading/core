import logging
import time
from datetime import datetime

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
        parser.add_argument('arg', nargs='?', default='compute_indicators_for_poloniex', type=str)

    def handle(self, *args, **options):
        logger.info("Starting data gaps restoration...")

        arg = options['arg']

        while True:
            fill_data_gaps(arg == 'force_fill_gaps')
            time.sleep(1)


def fill_data_gaps(force_fill=False):


    for ticker in ["*_USDT", "*_BTC"]:
        for index in ['close_price', 'open_price', 'high_price', 'low_price']:

            for key in database.keys(f"*{ticker}*PriceStorage*{index}*"):
                [ticker, exchange, storage_class, index] = key.decode("utf-8").split(":")

                start_score = missing_data.find_start_score(ticker, exchange, index)
                # end score is either 24hrs later or now() at the latest
                end_score = min([start_score+(12*24), TimeseriesStorage.score_from_timestamp(datetime.today().timestamp())])

                logger.debug(f"working on {ticker}:{exchange}:PVStorages:{index}..." +
                             f"starting at {TimeseriesStorage.datetime_from_score(start_score)}")

                missing_scores = missing_data.find_pv_storage_data_gaps(
                    ticker, exchange, index,
                    start_score, end_score=end_score)  # process only up to 1 day


                if missing_scores:
                    logger.warning(
                        "The followng scores could not be recovered and are still missing...\n" +
                        f"for key: {ticker}:{exchange}:PriceStorage:{index}" + "\n" +
                        str(missing_scores)
                    )

                if force_fill:
                    logger.warning("STARTING FORCE FILL OF THESE VALUES...")
                    logger.warning("!! THERE'S NO GOING BACK FROM HERE. DATA MAY WILL BE PERMAMENTLY CORRUPTED !!")
                    missing_data.force_plug_pv_storage_data_gaps(ticker, exchange, index, missing_scores)






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
            (datetime(2018, 9, 1).timestamp() - datetime(2017, 1, 1).timestamp()) / 300)  # this is Sep 1 2018
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

import logging
import time
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.TA import PRICE_INDEXES
from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
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

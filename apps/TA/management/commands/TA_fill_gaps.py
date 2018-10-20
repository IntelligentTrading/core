import logging
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.TA.storages.utils import missing_data
from settings.redis_db import database

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Redis Data gaps filler'

    def add_arguments(self, parser):
        parser.add_argument('arg', nargs='?', default='compute_indicators_for_poloniex', type=str)


    def handle(self, *args, **options):
        arg = options['arg']

        logger.info("Starting data gaps restoration...")

        today = datetime.now()
        start_datetime = datetime(today.year, today.month, today.day)

        start_datetime = datetime(2018, 6, 1)
        end_datetime = datetime(2018, 9, 1)
        assert start_datetime < end_datetime  # please go forward in time :)
        process_datetime = start_datetime

        for key in database.keys("*PriceStorage*"):
            [ticker, exchange, storage_class, index] = key.decode("utf-8").split(":")

            start_score = missing_data.find_start_score(ticker, exchange, index)

            missing_scores = missing_data.find_pv_storage_data_gaps(ticker, exchange, index, start_score)

            if missing_scores:
                logger.warning(
                    "The followng scores could not be recovered and are still missing...\n" +
                    f"for key: {ticker}:{exchange}:PriceStorage:{index}" + "\n" +
                    str(missing_scores)
                )
                break  # just one at a times for good measure :)

            if arg == 'force_fill_gaps':
                logger.warning("STARTING FORCE FILL OF THESE VALUES...")
                logger.warning("!! THERE'S NO GOING BACK FROM HERE. DATA MAY WILL BE PERMAMENTLY CORRUPTED !!")
                missing_data.force_plug_pv_storage_data_gaps(ticker, exchange, index, missing_scores)

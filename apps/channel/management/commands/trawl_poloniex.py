import logging
import schedule
import time

from django.core.management.base import BaseCommand

from settings import time_speed  # 1 / 10

from requests import get, RequestException

from apps.channel.models import ExchangeData
#from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume
from apps.indicator.models.price import get_currency_value_from_string
from apps.indicator.models.price_resampl import get_first_resampled_time

from settings import time_speed  # 1 / 10
from settings import USDT_COINS, BTC_COINS, POLONIEX

from settings import PERIODS_LIST, SHORT, MEDIUM, LONG

from taskapp.helpers import _pull_poloniex_data, _compute_and_save_indicators, _backtest_all_strategies

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    # Currently we use this command for debug only

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")
        SOURCE = 0

        #schedule.every().minute.do(_pull_poloniex_data, SOURCE )

        #logger.info("Getting ready to reevaluation all strategies...")
        #schedule.every().minute.do(_backtest_all_strategies)


        # @Alex
        # run resampling for all periods and calculate indicator values
        logger.info("Getting ready to recalculate all idicators...")
        for horizont_period in PERIODS_LIST:
            hours = (horizont_period / 60) / time_speed  # convert to hours

            if horizont_period in [SHORT, MEDIUM]:
                schedule.every(hours).hours.at("00:00").do(
                    _compute_and_save_indicators,
                    source=0,
                    resample_period=horizont_period

                )

            # if long period start exacly at the beginning of a day
            if horizont_period == LONG:
                schedule.every().day.at("00:00").do(
                    _compute_and_save_indicators,
                    source=0,
                    resample_period=horizont_period

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


import json
import logging
import schedule
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import BINANCE
from apps.channel.trigger_indicators import compute_and_save_indicators
from apps.indicator.models import Price, Volume
from apps.indicator.models.price import get_currency_value_from_string
from apps.indicator.models.price_resampl import get_n_last_resampl_df, get_first_resampled_time

from settings import time_speed  # 1 / 10
from settings import USDT_COINS, BTC_COINS
from settings import PERIODS_LIST, SHORT, MEDIUM, LONG

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Binance on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Binance...")

        schedule.every(1/time_speed).minutes.do(_pull_binance_data)

        # @Alex
        # run resampling for all periods and calculate indicator values
        # TODO synchronize the start with beginning of hours / days / etc

        ###### temporarily disable because Poloniex signals are still running ######
        # for hor_period in PERIODS_LIST:
        #     schedule.every(hor_period / time_speed).minutes.do(
        #         compute_and_save_indicators,
        #         {'period': hor_period, 'channel': BINANCE}
        #     )
        ###### temporarily disable because Poloniex signals are still running ######

        keep_going = True
        while keep_going:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.debug(str(e))
                logger.info("Binance Trawl shut down.")
                keep_going = False


def _pull_binance_data():
    try:
        logger.info("pulling Binance data...")
        req = get('https://api.binance.com/api/v1/ticker/24hr')

        data = req.json()
        timestamp = time.time()

        binance_data_point = ExchangeData.objects.create(
            source=BINANCE,
            data=json.dumps(data),
            timestamp=timestamp
        )
        logger.info("Saving Binance price, volume data...")
        _save_prices_and_volumes(data, timestamp)


    except RequestException:
        return 'Error to collect data from Binance'


def _save_prices_and_volumes(data, timestamp):
    for currency_pair in data:
        try:
            for currency_string in ["BTC", "ETH", "USDT"]:
                if currency_pair['symbol'].endswith(currency_string):
                    counter_currency_string = currency_string
                    counter_currency = get_currency_value_from_string(currency_string)
            assert counter_currency >= 0
            transaction_currency_string = currency_pair['symbol'].strip(counter_currency_string)
            assert len(transaction_currency_string) > 1 and len(transaction_currency_string) <= 6

            Price.objects.create(
                source=BINANCE,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                price=int(float(currency_pair['lastPrice']) * 10 ** 8),
                timestamp=timestamp
            )

            Volume.objects.create(
                source=BINANCE,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                volume=float(currency_pair['volume']),
                timestamp=timestamp
            )
        except Exception as e:
            logger.debug(str(e))

    logger.debug("Saved Binance price and volume data")

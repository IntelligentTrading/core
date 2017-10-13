import json
import logging
import time

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polls data from Poloniex on a regular interval"

    def handle(self, *args, **options):
        logger.info("Getting ready to trawl Poloniex...")

        import schedule
        import time

        def job():
            print("I'm working...")

        schedule.every(1).minutes.do(pull_poloniex_data)

        while True:
            schedule.run_pending()
            time.sleep(1)

        logger.info("Poloniex Trawl shut down.")


def pull_poloniex_data():
    try:
        req = get('https://poloniex.com/public?command=returnTicker')

        data = req.json()
        timestamp = time.time()

        poloniex_data_point = ExchangeData.objects.create(
            data=json.dumps(data),
            timestamp=timestamp
        )

        save_prices(data, timestamp)
        save_volumes(data, timestamp)

    except RequestException:
        return 'Error to collect data from Poloniex'


def save_prices(data, timestamp):
    try:
        usdt_btc = data.pop("USDT_BTC")
        Price.objects.create(
            source=POLONIEX,
            coin="BTC",
            satoshis=int(10 ** 8),
            usdt=float(usdt_btc['last']),
            timestamp=timestamp
        )
    except KeyError:
        logger.debug("missing BTC in Poloniex data")

    for currency_pair in data:
        if currency_pair.split('_')[0] == "BTC":
            Price.objects.create(
                source=POLONIEX,
                coin=currency_pair.split('_')[1],
                satoshis=int(float(data[currency_pair]['last']) * 10 ** 8),
                timestamp=timestamp
            )

    # trigger indicators


def save_volumes(data, timestamp):
    try:
        usdt_eth = data.pop("USDT_ETH")
        btc_eth = data.pop("USDT_ETH")
        Price.objects.create(
            source=POLONIEX,
            coin="ETH",
            satoshis=int(float(btc_eth['last']) * 10 ** 8),
            wei=int(10 ** 8),
            usdt=float(usdt_eth['last']),
            timestamp=timestamp
        )
    except KeyError:
        logger.debug("missing ETH in Poloniex data")

    for currency_pair in data:
        if currency_pair.split('_')[0] == "BTC":
            Volume.objects.create(
                source=POLONIEX,
                coin=currency_pair.split('_')[1],
                btc_volume=int(float(data[currency_pair]['volume']) * 10 ** 8)
            )

    # trigger indicators

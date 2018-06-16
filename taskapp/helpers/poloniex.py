import time
import logging
import json

from requests import get

from apps.channel.models import ExchangeData
from apps.indicator.models import Price, Volume
from apps.indicator.models.price import get_currency_value_from_string

from settings import POLONIEX

logger = logging.getLogger(__name__)


def _pull_poloniex_data():
    logger.info("pulling Poloniex data...")
    req = get('https://poloniex.com/public?command=returnTicker')

    data = req.json()
    timestamp = time.time()

    ExchangeData.objects.create(
        source=POLONIEX,
        data=json.dumps(data),
        timestamp=timestamp
    )
    logger.info("Saving Poloniex price, volume data...")
    _save_prices_and_volumes(data, timestamp, POLONIEX)


def _save_prices_and_volumes(data, timestamp, source):
    for currency_pair in data:
        try:
            counter_currency_string = currency_pair.split('_')[0]
            counter_currency = get_currency_value_from_string(counter_currency_string)
            # assert counter_currency >= 0
            transaction_currency_string = currency_pair.split('_')[1]
            # assert len(transaction_currency_string) > 1 and len(transaction_currency_string) <= 6

            Price.objects.create(
                source=source,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                price=int(float(data[currency_pair]['last']) * 10 ** 8),
                timestamp=timestamp
            )

            Volume.objects.create(
                source=source,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                volume=float(data[currency_pair]['baseVolume']),
                timestamp=timestamp
            )
        except Exception as e:
            logger.debug(str(e))

    logger.debug("Saved Poloniex price and volume data")

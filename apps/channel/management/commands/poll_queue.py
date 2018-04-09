import json
import logging
import time

from django.core.management.base import BaseCommand

from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models import Price, Volume

from apps.channel.incoming_queue import SqsListener



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Polls price data from the incoming queue"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll prices from the queue")

        # FIXME get sqs queue name from settings
        listener = SqsListener('itf-sqs-core-incoming-data-test', wait_time=5)
        listener.handler = process_message_from_queue
        listener.listen()


# * Standart Format
# symbols_info = [
#     {   'source': 'poloniex',
#         'category': 'price', # or 'volume'
#         'symbol': 'BTC/USDT' # LTC/BTC
#         'value': 12345678,
#         'timestamp': 1522066118.23
#     }, ...
# ]

def process_message_from_queue(message_body):
    body_dict = json.loads(message_body)
    exchange = json.loads(body_dict['Message'])

    # FIXME we need to add some filtering
    for item in exchange:
        logger.debug("Process: {category} for: {symbol} from: {source}".format(**item))
    
        source_code = next((code for code, source_text in SOURCE_CHOICES if source_text==item['source']), None)

        (transaction_currency, counter_curency_text) = item['symbol'].split('/')

        counter_currency_code = next((code for code, counter_currency in Price.COUNTER_CURRENCY_CHOICES if counter_currency==counter_curency_text), None)
        if None in (source_code, counter_currency_code):
            continue # skip this source or counter_currency

        if 'price' == item['category']:
            price = int(float(item['value']) * 10 ** 8) # convert to satoshi
            try:
                Price.objects.create(
                    source=source_code,
                    transaction_currency=transaction_currency,
                    counter_currency=counter_currency_code,
                    price=price,
                    timestamp=item['timestamp']
                )
                logger.debug(">>> Price saved: source={}, transaction_currency={}, counter_currency={}, price={}, timestamp={}".format(
                            source_code, transaction_currency, counter_currency_code, price, item['timestamp']))
            except Exception as e:
                logger.debug(">>>> Error saving Price for {}: {}".format(item['symbol'], e))


        elif 'volume' == item['category']:
            volume = float(item['value'])
            try:
                Volume.objects.create(
                    source=source_code,
                    transaction_currency=transaction_currency,
                    counter_currency=counter_currency_code,
                    volume=volume,
                    timestamp=item['timestamp']
                )
                logger.debug(">>> Volume saved: source={}, transaction_currency={}, counter_currency={}, volume={}, timestamp={}".format(
                            source_code, transaction_currency, counter_currency_code, volume, item['timestamp']))
            except Exception as e:
                logger.debug(">>>> Error saving Volume for {}: {}".format(item['symbol'], e))
    logger.debug("Message processed and saved")

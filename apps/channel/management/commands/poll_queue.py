import json
import logging
import time

from django.core.management.base import BaseCommand

#from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models import Price, Volume
from taskapp.helpers import get_source_name

from apps.channel.incoming_queue import SqsListener

from settings import INCOMING_SQS_QUEUE, SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Polls price data from the incoming queue"

    def handle(self, *args, **options):
        logger.info("Getting ready to poll prices from the queue")

        listener = SqsListener(INCOMING_SQS_QUEUE, wait_time=10)
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
    "Save SQS message to DB: Price and Volume"
    
    body_dict = json.loads(message_body)
    exchange = json.loads(body_dict['Message'])
    processed = []

    for item in exchange:
        #logger.debug("Save {category} for {symbol} from {source}".format(**item))
    
        source_code = next((code for code, source_text in SOURCE_CHOICES if source_text==item['source']), None)

        (transaction_currency, counter_curency_text) = item['symbol'].split('/')

        counter_currency_code = next((code for code, counter_currency in COUNTER_CURRENCY_CHOICES if counter_currency==counter_curency_text), None)
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
                processed.append("{}/{}".format(transaction_currency, counter_currency_code))
                #logger.debug(">>> Price saved: source={}, transaction_currency={}, counter_currency={}, price={}, timestamp={}".format(
                #            source_code, transaction_currency, counter_currency_code, price, item['timestamp']))
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
                #logger.debug(">>> Volume saved: source={}, transaction_currency={}, counter_currency={}, volume={}, timestamp={}".format(
                #            source_code, transaction_currency, counter_currency_code, volume, item['timestamp']))
            except Exception as e:
                logger.debug(">>>> Error saving Volume for {}: {}".format(item['symbol'], e))
    
    logger.debug("Message for {} saved to db. Coins: {}".format(get_source_name(source_code), ",".join(processed)))
    logger.info("Message for {} ({}) saved to db".format(get_source_name(source_code), len(processed)))

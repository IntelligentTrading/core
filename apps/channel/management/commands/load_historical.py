# import json
import logging
import re
import io
# #import time

import boto3
import pandas as pd

from django.core.management.base import BaseCommand

from settings import AWS_OPTIONS

# #from apps.channel.models.exchange_data import SOURCE_CHOICES
# from apps.indicator.models import Price, Volume
# from taskapp.helpers import get_source_name

# from apps.channel.incoming_queue import SqsListener

# from settings import INCOMING_SQS_QUEUE, SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Read historical data from s3 file.
            Filename in format: s3_bucket/exchange-currency-counter_currency.csv
            For example: /manage.py load_historical intelligenttrading-historical-dump/poloniex-BTC-USDT.csv
            The columns are: timestamp, open, high, low, close, volume
            """

    def add_arguments(self, parser):
        "filename like: binance-ADA-BNB.csv"
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        logger.info(f"Starting reading historical data from: {filename}")
     
        print(read_csv_from_s3(filename))


# helpers
def read_csv_from_s3(filename):
    match_filename = re.match(r'^([^/]+)\/([^-]+)\-([^-]+)\-([^.]+)\.csv$', filename)
    if not match_filename:
        logger.error("Bad filename format. Exiting")
        return None
    bucket_name, exchange, transaction_currency, counter_currency = match_filename.groups()
    logger.info(f"bucket: {bucket_name}, exchange: {exchange}, currency: {transaction_currency}, counter_currency: {counter_currency}")

    # resource = boto3.resource('s3')
    # bucket = resource.Bucket(s3_bucket_name)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name = 'us-east-1',
    )

    csv_obj = s3_client.get_object(Bucket=bucket_name, Key=f'{exchange}-{transaction_currency}-{counter_currency}.csv')
    colnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    history_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()), names=colnames, header=None)
    # Some checking
    assert history_df.timestamp.is_monotonic_increasing # ordered by timestamp
    assert history_df.close.min() > 0

    
    # filtering
    #history_df[history_df['timestamp']>1525620000000]


    
    # for fname in s3_client.list_objects(Bucket=bucket_name, Prefix='/')['Contents']:
    #     print(fname)

    # csv_obj = s3client.get_object(Bucket=s3_bucket_name, Key=f'{exchange}-{transaction_currency}-{counter_currency}.csv')
    # history_data = pd.read_csv(csv_obj['Body'])
    # print(history_data)
    return None


# # * Standart Format
# # symbols_info = [
# #     {   'source': 'poloniex',
# #         'category': 'price', # or 'volume'
# #         'symbol': 'BTC/USDT' # LTC/BTC
# #         'value': 12345678,
# #         'timestamp': 1522066118.23
# #     }, ...
# # ]

# def process_message_from_queue(message_body):
#     "Save SQS message to DB: Price and Volume"
    
#     body_dict = json.loads(message_body)
#     exchange = json.loads(body_dict['Message'])
#     processed = []

#     for item in exchange:
#         #logger.debug("Save {category} for {symbol} from {source}".format(**item))
    
#         source_code = next((code for code, source_text in SOURCE_CHOICES if source_text==item['source']), None)

#         (transaction_currency, counter_curency_text) = item['symbol'].split('/')

#         counter_currency_code = next((code for code, counter_currency in COUNTER_CURRENCY_CHOICES if counter_currency==counter_curency_text), None)
#         if None in (source_code, counter_currency_code):
#             continue # skip this source or counter_currency

#         if 'price' == item['category']:
#             price = int(float(item['value']) * 10 ** 8) # convert to satoshi
#             try:
#                 Price.objects.create(
#                     source=source_code,
#                     transaction_currency=transaction_currency,
#                     counter_currency=counter_currency_code,
#                     price=price,
#                     timestamp=item['timestamp']
#                 )
#                 processed.append("{}/{}".format(transaction_currency, counter_currency_code))
#                 #logger.debug(">>> Price saved: source={}, transaction_currency={}, counter_currency={}, price={}, timestamp={}".format(
#                 #            source_code, transaction_currency, counter_currency_code, price, item['timestamp']))
#             except Exception as e:
#                 logger.debug(">>>> Error saving Price for {}: {}".format(item['symbol'], e))


#         elif 'volume' == item['category']:
#             volume = float(item['value'])
#             try:
#                 Volume.objects.create(
#                     source=source_code,
#                     transaction_currency=transaction_currency,
#                     counter_currency=counter_currency_code,
#                     volume=volume,
#                     timestamp=item['timestamp']
#                 )
#                 #logger.debug(">>> Volume saved: source={}, transaction_currency={}, counter_currency={}, volume={}, timestamp={}".format(
#                 #            source_code, transaction_currency, counter_currency_code, volume, item['timestamp']))
#             except Exception as e:
#                 logger.debug(">>>> Error saving Volume for {}: {}".format(item['symbol'], e))
    
#     #logger.debug("Message for {} saved to db. Coins: {}".format(get_source_name(source_code), ",".join(processed)))
#     logger.info("Message for {} ({}) saved to db".format(get_source_name(source_code), len(processed)))

import datetime
import json
import logging
import os
import csv
import ast
# import re
# import io
import time
import sys

# import pandas as pd
from django.core.management.base import BaseCommand
from apps.indicator.models.price_history import PriceHistory

#from apps.channel.helpers import source_code_from_name, counter_currency_code_from_name
#from apps.channel.tickers import to_satoshi_int

from settings import BASE_DIR, COUNTER_CURRENCY_CHOICES, COUNTER_CURRENCIES, SOURCE_CHOICES



csv.field_size_limit(sys.maxsize)
class Command(BaseCommand):
    help = 'Read historical data from core "channel_exchangedata" from Core and Data app in csv format.'

    # def add_arguments(self, parser):
    #     "filename like: binance-ADA-BNB.csv"
    #     parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        ## import price history from Core app  channel exchange data csv
        #read_from_core_channel_exchange_data_poloniex()

        ## import price history from Data app  channel exchange dat csv
        #read_from_data_channel_exchange_data_all()


def read_from_data_channel_exchange_data_all():
    filename = 'datapp-data-1529604900941.csv' # Core App channel.exchange_data (poloniex)

    #print(f"Starting reading historical data from {filename} - lines: {file_len(filename)}")

    iter_rows = iter(getrow(filename))
    print(f"Columns:{next(iter_rows)}")  # Skipping the column names

    for idx, row in enumerate(iter_rows):
        (_, source_text, data, timestamp_str) = row # timestamp in itf format
        row_timestamp = float(timestamp_str) # timestamp in itf format

        source = get_source_code_from_exchange(source_text)
        data_dict = json.loads(data)

        prices = []
        i = 0
        for key, value in data_dict.items():
            try:
                transaction_currency, counter_currency = key.split("/")
            except:
                print(f"Skipped malformed coin: {key}")
                continue # skip malformed pairs
            if len(transaction_currency) > 6: # skip long coins
                print(f">>> Skipped long coin: {transaction_currency}")
                continue
            #print(f">>>> counter_cur: {counter_currency}")
            counter_currency_code = next((code for code, cc_text in COUNTER_CURRENCY_CHOICES if counter_currency == cc_text), None)
            if counter_currency_code is None:
                print(f">>>>Skip non-supported counter_cur: {counter_currency}")
                continue

            print(f"{idx}: {source} {key} {value['timestamp']/1000}")

            #import pdb; pdb.set_trace()

            price = PriceHistory(
                timestamp=datetime.datetime.utcfromtimestamp(float(value['timestamp'])/1000),
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency_code,
                close=to_satoshi(value['close']),
                open_p=to_satoshi(value['open']),
                high=to_satoshi(value['high']),
                low=to_satoshi(value['low']),
                volume=get_volume(value['baseVolume']),
            )
            prices.append(price)
            #print(price.__dict__)
            i += 1
            #break
        #break
        PriceHistory.objects.bulk_create(prices)
        print(f"Saved coins batch ({i}) from: {source} at {row_timestamp}")

def get_source_code_from_exchange(exchange):
    "return 0 for poloniex"
    return next((code for code, source_text in SOURCE_CHOICES if source_text == exchange), None)

def read_from_core_channel_exchange_data_poloniex():
    filename = 'core-dataexch-data-1529596368519.csv' # Core App channel.exchange_data (poloniex)

    #print(f"Starting reading historical data from {filename} - lines: {file_len(filename)}")

    iter_rows = iter(getrow(filename))
    print(f"Columns:{next(iter_rows)}")  # Skipping the column names
    for idx, row in enumerate(iter_rows):
        (_, source, data, timestamp_str) = row # timestamp in itf format
        timestamp = float(timestamp_str) # timestamp in itf format
        data_dict = ast.literal_eval(data)

        prices = []
        i = 0
        for key, value in data_dict.items():
            counter_currency, transaction_currency = key.split("_") # it switched for raw poloniex
            counter_currency_code = next(code for code, cc_text in COUNTER_CURRENCY_CHOICES if counter_currency == cc_text)
            print(f"{idx} - {key} - {timestamp}")

            price = PriceHistory(
                timestamp=datetime.datetime.utcfromtimestamp(timestamp),
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency_code,
                close=to_satoshi(float(value['last'])),
                volume=get_volume(value['quoteVolume']), # because trading pair is switched, we need quoteVolume, not basevolume
            )
            prices.append(price)
            print(price.__dict__)
            #return
            i += 1
            #break
        #break
        PriceHistory.objects.bulk_create(prices)
        print(f"Saved coins batch ({i}) from: {source} at {timestamp}")

# csv iterator
def getrow(filename):
    with open(os.path.join(BASE_DIR, filename), "r") as csvfile:
        for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
            yield row

def file_len(fname):
    i = 0
    with open(fname) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

def to_satoshi(value):
    try:
        return int(float(value) * 10 ** 8)
    except:
        return None

def get_volume(value):
    try:
        return float(value)
    except:
        return None



# def import_db_data_channel_exchangedata():
#     #start_time = time.time()
#     logger.info(f"Starting reading data from Data App")
#     records = ExchangeData.objects.order_by('timestamp').iterator()
#     #print(record.__dict__)
#     #source_txt = record.source
#     #print(source_txt)

#     j = 0
#     for record in records:
#         source = source_code_from_name(record.source)
#         print("ID:", record.id, "Source:", source)
#         for coin, coin_value in record.data.items():
#             print(f"record: {record.id}, counter: {j}, coin: {coin}")
#             j += 1
#             try:
#                 transaction_currency, counter_currency_txt  = coin.split("/")
#             except: # skip
#                 continue
#             #print(f"coin:{coin} tc:{transaction_currency} cc:{counter_currency_txt}")
#             if counter_currency_txt not in COUNTER_CURRENCIES:
#                 print("Skipping:", coin)
#                 continue
#             print(f"Processsing coin:{coin} tc:{transaction_currency} cc:{counter_currency_txt} from: {record.source}")

#             timestamp = coin_value['timestamp']/1000
#             counter_currency = counter_currency_code_from_name(counter_currency_txt)

#             print(coin_value)
#             # Dry run
#             # f"""
#             PriceHistory.objects.create(
#                 timestamp = {timestamp},
#                 source = {source},
#                 transaction_currency = {transaction_currency},
#                 counter_currency = {counter_currency},
#                 open_price = {to_satoshi_int(coin_value['open'])},
#                 high_price = {to_satoshi_int(coin_value['high'])},
#                 low_price = {to_satoshi_int(coin_value['low'])},
#                 close_price = {to_satoshi_int(coin_value['close'])},
#                 base_volume = {coin_value['baseVolume']},
#                 extra = 2,
#             """


#         #counter_currency_code = next((code for code, cc_text in COUNTER_CURRENCY_CHOICES if counter_text==cc_text), None)

#         # skip None Counter currency and check if it in CC list
#         #print(coin, transaction_currency, counter_currency_code)

#         #break

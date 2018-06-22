import logging
import time
import csv
import datetime
import os

import os.path
import boto3

import pandas as pd

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.indicator.models.price_history import PriceHistory

from settings import AWS_OPTIONS, SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES


logger = logging.getLogger(__name__)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)

EXCHANGE = 'binance'

# get_matching_s3_keys(bucket=bucket, prefix=f"{exchange}-"):
# for poloniex: IMPORT_FILES = ['poloniex-AMP-BTC.csv', 'poloniex-ARDR-BTC.csv', 'poloniex-BCH-BTC.csv', 'poloniex-BCH-ETH.csv', 'poloniex-BCH-USDT.csv', 'poloniex-BCN-BTC.csv', 'poloniex-BCN-XMR.csv', 'poloniex-BCY-BTC.csv', 'poloniex-BELA-BTC.csv', 'poloniex-BLK-BTC.csv', 'poloniex-BLK-XMR.csv', 'poloniex-BTC-USDT.csv', 'poloniex-BTCD-BTC.csv', 'poloniex-BTCD-XMR.csv', 'poloniex-BTS-BTC.csv', 'poloniex-BURST-BTC.csv', 'poloniex-CLAM-BTC.csv', 'poloniex-CVC-BTC.csv', 'poloniex-CVC-ETH.csv', 'poloniex-DASH-BTC.csv', 'poloniex-DASH-USDT.csv', 'poloniex-DASH-XMR.csv', 'poloniex-DCR-BTC.csv', 'poloniex-DGB-BTC.csv', 'poloniex-DOGE-BTC.csv', 'poloniex-EMC2-BTC.csv', 'poloniex-ETC-BTC.csv', 'poloniex-ETC-ETH.csv', 'poloniex-ETC-USDT.csv', 'poloniex-ETH-BTC.csv', 'poloniex-ETH-USDT.csv', 'poloniex-EXP-BTC.csv', 'poloniex-FCT-BTC.csv', 'poloniex-FLDC-BTC.csv', 'poloniex-FLO-BTC.csv', 'poloniex-GAME-BTC.csv', 'poloniex-GAS-BTC.csv', 'poloniex-GAS-ETH.csv', 'poloniex-GNO-BTC.csv', 'poloniex-GNO-ETH.csv', 'poloniex-GNT-BTC.csv', 'poloniex-GNT-ETH.csv', 'poloniex-GRC-BTC.csv', 'poloniex-HUC-BTC.csv', 'poloniex-LBC-BTC.csv', 'poloniex-LSK-BTC.csv', 'poloniex-LSK-ETH.csv', 'poloniex-LTC-BTC.csv', 'poloniex-LTC-USDT.csv', 'poloniex-LTC-XMR.csv', 'poloniex-MAID-BTC.csv', 'poloniex-MAID-XMR.csv', 'poloniex-NAV-BTC.csv', 'poloniex-NEOS-BTC.csv', 'poloniex-NMC-BTC.csv', 'poloniex-NXC-BTC.csv', 'poloniex-NXT-BTC.csv', 'poloniex-NXT-USDT.csv', 'poloniex-NXT-XMR.csv', 'poloniex-OMG-BTC.csv', 'poloniex-OMG-ETH.csv', 'poloniex-OMNI-BTC.csv', 'poloniex-PASC-BTC.csv', 'poloniex-PINK-BTC.csv', 'poloniex-POT-BTC.csv', 'poloniex-PPC-BTC.csv', 'poloniex-RADS-BTC.csv', 'poloniex-REP-BTC.csv', 'poloniex-REP-ETH.csv', 'poloniex-REP-USDT.csv', 'poloniex-RIC-BTC.csv', 'poloniex-SBD-BTC.csv', 'poloniex-SC-BTC.csv', 'poloniex-STEEM-BTC.csv', 'poloniex-STEEM-ETH.csv', 'poloniex-STORJ-BTC.csv', 'poloniex-STRAT-BTC.csv', 'poloniex-SYS-BTC.csv', 'poloniex-VIA-BTC.csv', 'poloniex-VRC-BTC.csv', 'poloniex-VTC-BTC.csv', 'poloniex-XBC-BTC.csv', 'poloniex-XCP-BTC.csv', 'poloniex-XEM-BTC.csv', 'poloniex-XLM-BTC.csv', 'poloniex-XLM-USDT.csv', 'poloniex-XMR-BTC.csv', 'poloniex-XMR-USDT.csv', 'poloniex-XPM-BTC.csv', 'poloniex-XRP-BTC.csv', 'poloniex-XRP-USDT.csv', 'poloniex-XVC-BTC.csv', 'poloniex-ZEC-BTC.csv', 'poloniex-ZEC-ETH.csv', 'poloniex-ZEC-USDT.csv', 'poloniex-ZEC-XMR.csv', 'poloniex-ZRX-BTC.csv', 'poloniex-ZRX-ETH.csv']
IMPORT_FILES = ['binance-ADA-BNB.csv', 'binance-ADA-BTC.csv', 'binance-ADA-ETH.csv', 'binance-ADA-USDT.csv', 'binance-ADX-BNB.csv', 'binance-ADX-BTC.csv', 'binance-ADX-ETH.csv', 'binance-AE-BNB.csv', 'binance-AE-BTC.csv', 'binance-AE-ETH.csv', 'binance-AION-BNB.csv', 'binance-AION-BTC.csv', 'binance-AION-ETH.csv', 'binance-AMB-BNB.csv', 'binance-AMB-BTC.csv', 'binance-AMB-ETH.csv', 'binance-APPC-BNB.csv', 'binance-APPC-BTC.csv', 'binance-APPC-ETH.csv', 'binance-ARK-BTC.csv', 'binance-ARK-ETH.csv', 'binance-ARN-BTC.csv', 'binance-ARN-ETH.csv', 'binance-AST-BTC.csv', 'binance-AST-ETH.csv', 'binance-BAT-BNB.csv', 'binance-BAT-BTC.csv', 'binance-BAT-ETH.csv', 'binance-BCD-BTC.csv', 'binance-BCD-ETH.csv', 'binance-BCH-BNB.csv', 'binance-BCH-BTC.csv', 'binance-BCH-ETH.csv', 'binance-BCH-USDT.csv', 'binance-BCPT-BNB.csv', 'binance-BCPT-BTC.csv', 'binance-BCPT-ETH.csv', 'binance-BLZ-BNB.csv', 'binance-BLZ-BTC.csv', 'binance-BLZ-ETH.csv', 'binance-BNB-BTC.csv', 'binance-BNB-ETH.csv', 'binance-BNB-USDT.csv', 'binance-BNT-BTC.csv', 'binance-BNT-ETH.csv', 'binance-BQX-BTC.csv', 'binance-BQX-ETH.csv', 'binance-BRD-BNB.csv', 'binance-BRD-BTC.csv', 'binance-BRD-ETH.csv', 'binance-BTC-USDT.csv', 'binance-BTG-BTC.csv', 'binance-BTG-ETH.csv', 'binance-BTS-BNB.csv', 'binance-BTS-BTC.csv', 'binance-BTS-ETH.csv', 'binance-CDT-BTC.csv', 'binance-CDT-ETH.csv', 'binance-CHAT-BTC.csv', 'binance-CHAT-ETH.csv', 'binance-CLOAK-BTC.csv', 'binance-CLOAK-ETH.csv', 'binance-CMT-BNB.csv', 'binance-CMT-BTC.csv', 'binance-CMT-ETH.csv', 'binance-CND-BNB.csv', 'binance-CND-BTC.csv', 'binance-CND-ETH.csv', 'binance-DASH-BTC.csv', 'binance-DASH-ETH.csv', 'binance-DGD-BTC.csv', 'binance-DGD-ETH.csv', 'binance-DLT-BNB.csv', 'binance-DLT-BTC.csv', 'binance-DLT-ETH.csv', 'binance-DNT-BTC.csv', 'binance-DNT-ETH.csv', 'binance-EDO-BTC.csv', 'binance-EDO-ETH.csv', 'binance-ELF-BTC.csv', 'binance-ELF-ETH.csv', 'binance-ENG-BTC.csv', 'binance-ENG-ETH.csv', 'binance-ENJ-BTC.csv', 'binance-ENJ-ETH.csv', 'binance-EOS-BTC.csv', 'binance-EOS-ETH.csv', 'binance-ETC-BTC.csv', 'binance-ETC-ETH.csv', 'binance-ETH-BTC.csv', 'binance-ETH-USDT.csv', 'binance-EVX-BTC.csv', 'binance-EVX-ETH.csv', 'binance-FUEL-BTC.csv', 'binance-FUEL-ETH.csv', 'binance-FUN-BTC.csv', 'binance-FUN-ETH.csv', 'binance-GAS-BTC.csv', 'binance-GNT-BNB.csv', 'binance-GNT-BTC.csv', 'binance-GNT-ETH.csv', 'binance-GRS-BTC.csv', 'binance-GRS-ETH.csv', 'binance-GTO-BNB.csv', 'binance-GTO-BTC.csv', 'binance-GTO-ETH.csv', 'binance-GVT-BTC.csv', 'binance-GVT-ETH.csv', 'binance-GXS-BTC.csv', 'binance-GXS-ETH.csv', 'binance-HSR-BTC.csv', 'binance-HSR-ETH.csv', 'binance-ICN-BTC.csv', 'binance-ICN-ETH.csv', 'binance-ICX-BNB.csv', 'binance-ICX-BTC.csv', 'binance-ICX-ETH.csv', 'binance-INS-BTC.csv', 'binance-INS-ETH.csv', 'binance-IOST-BTC.csv', 'binance-IOST-ETH.csv', 'binance-IOTA-BNB.csv', 'binance-IOTA-BTC.csv', 'binance-IOTA-ETH.csv', 'binance-KMD-BTC.csv', 'binance-KMD-ETH.csv', 'binance-KNC-BTC.csv', 'binance-KNC-ETH.csv', 'binance-LEND-BTC.csv', 'binance-LEND-ETH.csv', 'binance-LINK-BTC.csv', 'binance-LINK-ETH.csv', 'binance-LOOM-BNB.csv', 'binance-LOOM-BTC.csv', 'binance-LOOM-ETH.csv', 'binance-LRC-BTC.csv', 'binance-LRC-ETH.csv', 'binance-LSK-BNB.csv', 'binance-LSK-BTC.csv', 'binance-LSK-ETH.csv', 'binance-LTC-BNB.csv', 'binance-LTC-BTC.csv', 'binance-LTC-ETH.csv', 'binance-LTC-USDT.csv', 'binance-LUN-BTC.csv', 'binance-LUN-ETH.csv', 'binance-MANA-BTC.csv', 'binance-MANA-ETH.csv', 'binance-MCO-BNB.csv', 'binance-MCO-BTC.csv', 'binance-MCO-ETH.csv', 'binance-MDA-BTC.csv', 'binance-MDA-ETH.csv', 'binance-MOD-BTC.csv', 'binance-MOD-ETH.csv', 'binance-MTH-BTC.csv', 'binance-MTH-ETH.csv', 'binance-MTL-BTC.csv', 'binance-MTL-ETH.csv', 'binance-NAV-BNB.csv', 'binance-NAV-BTC.csv', 'binance-NAV-ETH.csv', 'binance-NCASH-BNB.csv', 'binance-NCASH-BTC.csv', 'binance-NCASH-ETH.csv', 'binance-NEBL-BNB.csv', 'binance-NEBL-BTC.csv', 'binance-NEBL-ETH.csv', 'binance-NEO-BNB.csv', 'binance-NEO-BTC.csv', 'binance-NEO-ETH.csv', 'binance-NEO-USDT.csv', 'binance-NULS-BNB.csv', 'binance-NULS-BTC.csv', 'binance-NULS-ETH.csv', 'binance-OAX-BTC.csv', 'binance-OAX-ETH.csv', 'binance-OMG-BTC.csv', 'binance-OMG-ETH.csv', 'binance-ONT-BNB.csv', 'binance-ONT-BTC.csv', 'binance-ONT-ETH.csv', 'binance-OST-BNB.csv', 'binance-OST-BTC.csv', 'binance-OST-ETH.csv', 'binance-PIVX-BNB.csv', 'binance-PIVX-BTC.csv', 'binance-PIVX-ETH.csv', 'binance-POA-BNB.csv', 'binance-POA-BTC.csv', 'binance-POA-ETH.csv', 'binance-POE-BTC.csv', 'binance-POE-ETH.csv', 'binance-POWR-BNB.csv', 'binance-POWR-BTC.csv', 'binance-POWR-ETH.csv', 'binance-PPT-BTC.csv', 'binance-PPT-ETH.csv', 'binance-QLC-BNB.csv', 'binance-QLC-BTC.csv', 'binance-QLC-ETH.csv', 'binance-QSP-BNB.csv', 'binance-QSP-BTC.csv', 'binance-QSP-ETH.csv', 'binance-QTUM-BNB.csv', 'binance-QTUM-BTC.csv', 'binance-QTUM-ETH.csv', 'binance-QTUM-USDT.csv', 'binance-RCN-BNB.csv', 'binance-RCN-BTC.csv', 'binance-RCN-ETH.csv', 'binance-RDN-BNB.csv', 'binance-RDN-BTC.csv', 'binance-RDN-ETH.csv', 'binance-REQ-BTC.csv', 'binance-REQ-ETH.csv', 'binance-RLC-BNB.csv', 'binance-RLC-BTC.csv', 'binance-RLC-ETH.csv', 'binance-RPX-BNB.csv', 'binance-RPX-BTC.csv', 'binance-RPX-ETH.csv', 'binance-SALT-BTC.csv', 'binance-SALT-ETH.csv', 'binance-SNGLS-BTC.csv', 'binance-SNGLS-ETH.csv', 'binance-SNM-BTC.csv', 'binance-SNM-ETH.csv', 'binance-SNT-BTC.csv', 'binance-SNT-ETH.csv', 'binance-STEEM-BNB.csv', 'binance-STEEM-BTC.csv', 'binance-STEEM-ETH.csv', 'binance-STORJ-BTC.csv', 'binance-STORJ-ETH.csv', 'binance-STORM-BNB.csv', 'binance-STORM-BTC.csv', 'binance-STORM-ETH.csv', 'binance-STRAT-BTC.csv', 'binance-STRAT-ETH.csv', 'binance-SUB-BTC.csv', 'binance-SUB-ETH.csv', 'binance-SYS-BNB.csv', 'binance-SYS-BTC.csv', 'binance-SYS-ETH.csv', 'binance-TNB-BTC.csv', 'binance-TNB-ETH.csv', 'binance-TNT-BTC.csv', 'binance-TNT-ETH.csv', 'binance-TRIG-BNB.csv', 'binance-TRIG-BTC.csv', 'binance-TRIG-ETH.csv', 'binance-TRX-BTC.csv', 'binance-TRX-ETH.csv', 'binance-VEN-BNB.csv', 'binance-VEN-BTC.csv', 'binance-VEN-ETH.csv', 'binance-VIA-BNB.csv', 'binance-VIA-BTC.csv', 'binance-VIA-ETH.csv', 'binance-VIB-BTC.csv', 'binance-VIB-ETH.csv', 'binance-VIBE-BTC.csv', 'binance-VIBE-ETH.csv', 'binance-WABI-BNB.csv', 'binance-WABI-BTC.csv', 'binance-WABI-ETH.csv', 'binance-WAN-BNB.csv', 'binance-WAN-BTC.csv', 'binance-WAN-ETH.csv', 'binance-WAVES-BNB.csv', 'binance-WAVES-BTC.csv', 'binance-WAVES-ETH.csv', 'binance-WINGS-BTC.csv', 'binance-WINGS-ETH.csv', 'binance-WPR-BTC.csv', 'binance-WPR-ETH.csv', 'binance-WTC-BNB.csv', 'binance-WTC-BTC.csv', 'binance-WTC-ETH.csv', 'binance-XEM-BNB.csv', 'binance-XEM-BTC.csv', 'binance-XEM-ETH.csv', 'binance-XLM-BNB.csv', 'binance-XLM-BTC.csv', 'binance-XLM-ETH.csv', 'binance-XMR-BTC.csv', 'binance-XMR-ETH.csv', 'binance-XRB-BNB.csv', 'binance-XRB-BTC.csv', 'binance-XRB-ETH.csv', 'binance-XRP-BTC.csv', 'binance-XRP-ETH.csv', 'binance-XRP-USDT.csv', 'binance-XVG-BTC.csv', 'binance-XVG-ETH.csv', 'binance-XZC-BNB.csv', 'binance-XZC-BTC.csv', 'binance-XZC-ETH.csv', 'binance-YOYOW-BNB.csv', 'binance-YOYOW-BTC.csv', 'binance-YOYOW-ETH.csv', 'binance-ZEC-BTC.csv', 'binance-ZEC-ETH.csv', 'binance-ZIL-BNB.csv', 'binance-ZIL-BTC.csv', 'binance-ZIL-ETH.csv', 'binance-ZRX-BTC.csv', 'binance-ZRX-ETH.csv']

ALREADY_IMPORTED = []
TO_TIMESTAMP = 1523015897.999


class Command(BaseCommand):
    help = "Load data from csv to pricehistory"

    def handle(self, *args, **options):
        bucket = 'intelligenttrading-historical-dump'
        exchange = EXCHANGE
        print(f"> Getting ready to load csv for {exchange}")
        start = time.time()

        #for file_name in get_matching_s3_keys(bucket=bucket, prefix=f"{exchange}-"):
        for file_no, file_name in enumerate(IMPORT_FILES):
            if skip_this_file(file_name):
                print(f"> Skip: {file_name}")
                continue
            else:
                print(f"\n{file_no}> Importing: {file_name}")
            #    file_name = 'poloniex-BTC-USDT.csv'
            # file_name = 'binance-ETH-BTC.csv'
            
                create_file_from_S3_Bucket(bucket, file_name)
                import_historical_prices_from_csv(file_name=file_name, from_timestamp=None, to_timestamp=TO_TIMESTAMP, do_not_write=False)
                os.remove(file_name)

        print(f"Exec time {time.time() - start} seconds")


def aws_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1',
    )

def aws_client(resource_type):
    return boto3.client(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1',
    )

def create_file_from_S3_Bucket(bucket_name, file_name):
    s3 = aws_resource('s3')
    print(f"> Download file: {file_name}")
    try:
        s3.Bucket(bucket_name).download_file(file_name, file_name)
    except Exception as e:
        print(f"> The object does not exist. {e}")



def import_historical_prices_from_csv(file_name, from_timestamp=None, to_timestamp=None, do_not_write=False):
    # from_timestamp (and to_) in ms, like 1483239900000, not inclusive
    #poloniex-BTC-USDT.csv -> 0 BTC 2
    (source_txt, transaction_currency, cc_txt) = os.path.splitext(file_name)[0].split("-")
    source = next((code for code, source_text in SOURCE_CHOICES if source_text == source_txt), None)
    counter_currency = next((code for code, cc_text in COUNTER_CURRENCY_CHOICES if cc_text == cc_txt), None)
    print(f"> Importing {file_name}: source: {source}, transaction_currency: {transaction_currency}, counter_currency: {counter_currency}")

    for chunk_df in pd.read_csv(file_name, names=["timestamp", "open", "high", "low", "close", "volume"], float_precision='round_trip', chunksize=500):
        prices = []
        for item in chunk_df.itertuples():
            (index, timestamp, openp, high, low, close, volume) = item
            #import pdb; pdb.set_trace()
            if from_timestamp and int(timestamp) <= int(from_timestamp)*1000:
                #print(f"skipping f: {timestamp})")
                print('f', end='')
                continue # skip items older than from_timestamp
            elif to_timestamp and int(timestamp) > int(to_timestamp)*1000:
                #print(f"skipping t: {timestamp})")
                print('t', end='')
                continue # skip items older than from_timestamp
            if do_not_write:
                pass
                #print(f"Sim DB write>t_cur:{transaction_currency},c_cur:{counter_currency},source:{source},timestamp:{datetime.datetime.utcfromtimestamp(float(timestamp)/1000.0)},ohlcv:{(openp, high, low, close, volume)}, tmstmpt:{timestamp}")
            price = PriceHistory(
                timestamp=datetime.datetime.utcfromtimestamp(float(timestamp)/1000.0),
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency,
                open_p=to_satoshi(openp),
                high=to_satoshi(high),
                low=to_satoshi(low),
                close=to_satoshi(close),
            )
            # if do_not_write:
            #     print(f"Price: {price.__dict__}")
            prices.append(price)
            print('.', end='')
        print('*', end='')
        if do_not_write:
            pass
#            print(f"Prices: {prices}")
        else:
            PriceHistory.objects.bulk_create(prices)
    print('')

def get_matching_s3_keys(bucket, prefix='', suffix=''):
    s3 = aws_client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break



def skip_this_file(file_name):
    # we already imported this
    if file_name in ALREADY_IMPORTED:
        print(f"> {file_name} already imported")
        return True
    (source_txt, transaction_currency, cc_txt) = os.path.splitext(file_name)[0].split("-")
    # we don't support this counter_currency
    counter_currency = next((cc_text for _, cc_text in COUNTER_CURRENCY_CHOICES if cc_text == cc_txt), None)
    if counter_currency is None:
        print(f"> {file_name} unsuported counter currency")
        return True
    else:
        return False


def to_satoshi(value):
    try:
        return int(float(value) * 10 ** 8)
    except:
        return None

# data was collected with ccxts fetch_ohlcv method

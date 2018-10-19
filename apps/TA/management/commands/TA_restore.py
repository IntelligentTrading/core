import logging
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
from settings.redis_db import database
from apps.indicator.models.price_history import PriceHistory
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, default_price_indexes, default_volume_indexes

logger = logging.getLogger(__name__)

try:
    earliest_price_timestamp = int(float(
        database.zrangebyscore("BTC:bittrex:PriceStorage:close_price", 0, "inf", 0, 1)[0].decode("utf-8").split(":")[
            0]))
except:
    earliest_price_timestamp = int(time.time())


class Command(BaseCommand):
    help = 'Run Redis Subscribers for TA'

    def handle(self, *args, **options):
        logger.info("Starting TA restore script.")

        # jan_1_2017_unix = 1483228800

        ### PULL PRICE HISTORY RECORDS FROM CORE PRICE HISTORY DATABASE ###

        today = datetime.now()
        start_day = datetime(today.year, today.month, today.day)

        start_day = datetime(2018, 9, 29)
        end_day = datetime(2017, 1, 1, 0, 0)
        process_day = start_day

        while process_day > end_day:
            process_day -= timedelta(days=1)
            price_history_objects = PriceHistory.objects.filter(
                timestamp__gte=process_day,
                timestamp__lt=process_day+timedelta(days=1)
            )

            pipeline = database.pipeline()  # transaction=False

            for ph_object in price_history_objects:
                # batch_num += 1

                if ph_object.transaction_currency not in transaction_currencies:
                    continue

                ticker = f'{ph_object.transaction_currency}_{ph_object.get_counter_currency_display()}'
                exchange = str(ph_object.get_source_display())
                unix_timestamp = int(ph_object.timestamp.timestamp())


                # SAVE VALUES IN REDIS USING PriceVolumeHistoryStorage OBJECT
                # CREATE OBJECT FOR STORAGE
                pv_storage = PriceVolumeHistoryStorage(
                    ticker=ticker,
                    exchange=exchange,
                    timestamp=unix_timestamp
                )

                if ph_object.open_p and ph_object.open_p > 0:
                    pv_storage.index = "open_price"
                    pv_storage.value = ph_object.open_p
                    pipeline = pv_storage.save(publish=True, pipeline=pipeline)

                if ph_object.high and ph_object.high > 0:
                    pv_storage.index = "high_price"
                    pv_storage.value = ph_object.high
                    pipeline = pv_storage.save(publish=True, pipeline=pipeline)

                if ph_object.low and ph_object.low > 0:
                    pv_storage.index = "low_price"
                    pv_storage.value = ph_object.low
                    pipeline = pv_storage.save(publish=True, pipeline=pipeline)

                if ph_object.close and ph_object.close > 0:
                    pv_storage.index = "close_price"
                    pv_storage.value = ph_object.close
                    pipeline = pv_storage.save(publish=True, pipeline=pipeline)

                if ph_object.volume and ph_object.volume > 0:
                    pv_storage.index = "close_volume"
                    pv_storage.value = ph_object.volume
                    pipeline = pv_storage.save(publish=False, pipeline=pipeline)

            database_response = pipeline.execute()
            logger.debug(f"{sum(database_response)} values added to Redis")

        ### END PULL OF PRICE HISTORY RECORDS ###


### RESAMPLE PRICES TO 5 MIN PRICE STORAGE RECORDS ###
def price_history_to_price_storage():
    start_score = processing_score = 0
    end_score = TimeseriesStorage.score_from_timestamp((datetime.today() - timedelta(hours=2)).timestamp())

    while processing_score < end_score:
        processing_score += 1





### END RESAMPLE FOR PRICE STORAGE RECORDS ###







transaction_currencies = [
    'XVG', 'IOTX', 'LTC', 'YOYOW', 'STR', 'TRX', 'ADA', 'CDT', 'VET', 'KEY', 'HOT', 'AGI', 'XMR', 'LEND', 'DENT',
    'NPXS', 'ZIL', 'XRP', 'IOST', 'EOS', 'VRC', 'ETH', 'ETC', 'NCASH', 'AST', 'RPX', 'VIB', 'ZRX', 'DGB', 'BTC', 'SC',
    'MFT', 'GTO', 'XEM', 'DASH', 'DOGE', 'XLM', 'FCT', 'BAT', 'QKC', 'POE', 'ENJ', 'FUN', 'STRAT', 'ICX', 'BCN', 'TNB',
    'CHAT', 'DOCK', 'REQ', 'IOTA', 'STORM', 'TNT', 'SNT', 'FUEL', 'BCH', 'LSK', 'OMG', 'BTS', 'WPR', 'ZEC', 'GAME',
    'MTH', 'OST', 'RCN', 'REP'
]
counter_currencies = [
    'BTC', 'ETH', 'USDT'
]

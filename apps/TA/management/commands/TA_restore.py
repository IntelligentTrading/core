import logging
import time
from datetime import datetime

from django.core.management.base import BaseCommand
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
        # timestamp = jan_1_2017 = datetime(2017, 1, 1)
        # timestamp_unix = int(timestamp.timestamp())

        PriceHistory.objects.order_by("timestamp").count()


        year, month = 2017, 1
        start_date = jan_1_2017 = datetime(year, month, 1, 0, 0)

        # batch_num = 0
        # batch_size = 500
        # batch_num_stop = 1  # set to -1 for infinity

        # all_price_history = PriceHistory.objects.order_by("timestamp")
        # all_price_history_count = all_price_history.count()

        while month <= 12:
            month += 1
            all_price_history = PriceHistory.objects.filter(timestamp__year=year, timestamp__month=month)

        # while (batch_num * batch_size < all_price_history_count) and not (batch_num == batch_num_stop):

            pipeline = database.pipeline()  # transaction=False

            for ph_object in all_price_history:
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
                    pipeline = pv_storage.save(publish=True, pipeline=pipeline)

            database_response = pipeline.execute()
            logger.debug(f"{sum(database_response)} values added to Redis")


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

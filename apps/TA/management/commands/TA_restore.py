import logging
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from apps.TA.management.commands.TA_fill_gaps import price_history_to_price_storage
from apps.TA.storages.abstract.ticker_subscriber import timestamp_is_near_5min
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, default_price_indexes
from apps.common.utilities.multithreading import multithread_this_shit
from settings import BTC, USDT, BINANCE
from settings.redis_db import database
from apps.indicator.models.price_history import PriceHistory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Redis Data Restore from SQL'

    def handle(self, *args, **options):
        logger.info("Starting TA restore script...")

        start_datetime = datetime(2018, 1, 1)
        end_datetime = datetime.today()

        restore_db_to_redis(start_datetime, end_datetime)

        from apps.TA.management.commands.TA_fill_gaps import fill_data_gaps
        fill_data_gaps(SQL_fill=True, force_fill=False)
        fill_data_gaps(SQL_fill=False, force_fill=False)


def restore_db_to_redis(start_datetime, end_datetime):
    if start_datetime > end_datetime:  # please go forward in time :)
        return

    process_datetime = start_datetime

    num_hours_per_query = 4

    while process_datetime < end_datetime:
        process_datetime += timedelta(hours=num_hours_per_query)

        logger.info(f"restoring past {num_hours_per_query} hours data to {process_datetime}")

        price_history_objects = PriceHistory.objects.filter(
            timestamp__gte=process_datetime - timedelta(hours=num_hours_per_query),
            timestamp__lt=process_datetime,
            source=BINANCE,  # Binance only for now

            transaction_currency="BTC",  #temp setting
            counter_currency=USDT,  # temp setting

            # counter_currency__in=[BTC, USDT]
        )

        results = multithread_this_shit(save_pv_histories_to_redis, price_history_objects)
        try:
            total_results = sum([sum(result) for result in results])
        except Exception as e:
            # logger.debug("couldn't sum all of it: " + str(e))
            total_results = 'unknown'

        # for ph_object in price_history_objects:
        #     if ph_object.transaction_currency not in transaction_currencies:
        #         continue
        #     pipeline = save_pv_histories_to_redis(ph_object)
        # database_response = pipeline.execute()
        # total_results = sum(database_response)

        logger.info(f"{total_results} values added to Redis")

        # if total_results < 4*60*5: #  minute data for 1 ticker
        #     continue
        #
        # price_history_to_price_storage(
        #     ticker_exchanges=[
        #         (f'{pho.transaction_currency}_{pho.get_counter_currency_display()}', pho.get_source_display())
        #         # (ticker, exchange) as strings
        #         for pho in price_history_objects
        #     ],
        #     start_score=TimeseriesStorage.score_from_timestamp(
        #         (process_datetime - timedelta(hours=num_hours_per_query)).timestamp()
        #     ),
        #     end_score=TimeseriesStorage.score_from_timestamp(process_datetime.timestamp())
        # )


### PULL PRICE HISTORY RECORDS FROM CORE PRICE HISTORY DATABASE ###
def save_pv_histories_to_redis(ph_object, pipeline=None):
    if ph_object.source is not BINANCE or ph_object.counter_currency not in [BTC, USDT]:
        return pipeline or [0]

    using_local_pipeline = (not pipeline)

    if using_local_pipeline:
        pipeline = database.pipeline()  # transaction=False

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

    publish_close_price = timestamp_is_near_5min(unix_timestamp)

    if ph_object.volume and ph_object.volume > 0:
        pv_storage.index = "close_volume"
        pv_storage.value = ph_object.volume
        pipeline = pv_storage.save(publish=publish_close_price, pipeline=pipeline)

    if ph_object.open_p and ph_object.open_p > 0:
        pv_storage.index = "open_price"
        pv_storage.value = ph_object.open_p
        pipeline = pv_storage.save(publish=False, pipeline=pipeline)

    if ph_object.high and ph_object.high > 0:
        pv_storage.index = "high_price"
        pv_storage.value = ph_object.high
        pipeline = pv_storage.save(publish=False, pipeline=pipeline)

    if ph_object.low and ph_object.low > 0:
        pv_storage.index = "low_price"
        pv_storage.value = ph_object.low
        pipeline = pv_storage.save(publish=False, pipeline=pipeline)

    # always run 'close_price' index last
    # why? when it saves, it triggers price storage to resample
    # after resampling history indexes are deleted
    # so all others should be available for resampling before being deleted

    if ph_object.close and ph_object.close > 0:
        pv_storage.index = "close_price"
        pv_storage.value = ph_object.close
        pipeline = pv_storage.save(publish=True, pipeline=pipeline)

    if using_local_pipeline:
        return pipeline.execute()
    else:
        return pipeline


### END PULL OF PRICE HISTORY RECORDS ###
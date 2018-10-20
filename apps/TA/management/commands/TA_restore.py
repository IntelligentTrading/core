import logging
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
from apps.common.utilities.multithreading import start_new_thread, multithread_this_shit
from settings import BTC, USDT, BINANCE
from settings.redis_db import database
from apps.indicator.models.price_history import PriceHistory
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, default_price_indexes, default_volume_indexes

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Redis Data Restore from SQL'

    def handle(self, *args, **options):
        logger.info("Starting TA restore script...")

        today = datetime.now()
        start_datetime = datetime(today.year, today.month, today.day)

        start_datetime = datetime(2018, 1, 1)
        end_datetime = datetime.today()
        assert start_datetime < end_datetime  # please go forward in time :)
        process_datetime = start_datetime

        num_hours_per_query = 4

        while process_datetime < end_datetime:
            process_datetime += timedelta(hours=num_hours_per_query)

            logger.debug(f"restoring past {num_hours_per_query} hours data to {process_datetime}")

            price_history_objects = PriceHistory.objects.filter(
                timestamp__gte=process_datetime - timedelta(hours=1),
                timestamp__lt=process_datetime,
                source=BINANCE,  # Binance only for now
                counter_currency__in=[BTC, USDT]
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

            logger.debug(f"{total_results} values added to Redis")

            price_history_to_price_storage(
                ticker_exchanges=[
                    (f'{pho.transaction_currency}_{pho.get_counter_currency_display()}', pho.get_source_display())
                    # (ticker, exchange) as strings
                    for pho in price_history_objects
                ],
                start_score=TimeseriesStorage.score_from_timestamp(
                    (process_datetime - timedelta(hours=num_hours_per_query)).timestamp()
                ),
                end_score=TimeseriesStorage.score_from_timestamp(process_datetime.timestamp())
            )

        from apps.TA.management.commands.TA_fill_gaps import fill_data_gaps
        fill_data_gaps()



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

    if ph_object.volume and ph_object.volume > 0:
        pv_storage.index = "close_volume"
        pv_storage.value = ph_object.volume
        pipeline = pv_storage.save(publish=False, pipeline=pipeline)

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


### RESAMPLE PRICES TO 5 MIN PRICE STORAGE RECORDS ###
# @start_new_thread
def price_history_to_price_storage(ticker_exchanges, start_score=None, end_score=None):
    from apps.TA.storages.utils.pv_resampling import generate_pv_storages

    if not start_score:
        # start_score = 0  # this is jan 1 2017
        start_score = int(
            (datetime(2018, 9, 1).timestamp() - datetime(2017, 1, 1).timestamp()) / 300)  # this is Sep 1 2018
    processing_score = start_score

    if not end_score:
        end_score = TimeseriesStorage.score_from_timestamp((datetime.today() - timedelta(hours=2)).timestamp())

    logger.debug(f"starting price resampling for scores {start_score} to {end_score}")

    while processing_score < end_score:
        processing_score += 1

        for ticker, exchange in ticker_exchanges:

            for index in default_price_indexes:
                if generate_pv_storages(ticker, exchange, index, processing_score):
                    if index == "close_price":
                        from apps.TA.storages.utils.memory_cleaner import clear_pv_history_values
                        clear_pv_history_values(ticker, exchange, processing_score)

    # returns nothing - can be threaded with collection of results
### END RESAMPLE FOR PRICE STORAGE RECORDS ###

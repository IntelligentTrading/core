import logging
import time

from apps.indicator.models.sma import SMA_LIST
from settings import STAGE
from settings.redis_db import database

logger = logging.getLogger(__name__)


def redisCleanup():

    try:
        do_not_disturb = bool(int(database.get("working on old stuff").decode("utf-8")))
    except:
        database.set("working on old stuff", 0)
        do_not_disturb = False

    if do_not_disturb:
        return

    logger.info("I'M CLEANING REDIS !!!")

    now_timestamp = int(time.time())

    # PriceVolumeHistoryStorage
    # delete all values 2 hours old or older
    old_for_pv_history_timestamp = now_timestamp - (3600 * 2)  # 2 hours

    from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage
    old_score = PriceVolumeHistoryStorage.score_from_timestamp(old_for_pv_history_timestamp)

    pv_history_keys = database.keys(f'*:PriceVolumeHistoryStorage:*')
    for pv_history_key in pv_history_keys:
        try:
            database.zremrangebyscore(pv_history_key, 0, old_score)
        except Exception as e:
            logger.error(str(e))


    #PriceVolumeHistoryStorage
    from datetime import datetime, timedelta
    from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage
    old_score = TimeseriesStorage.score_from_timestamp(datetime(2017, 1, 1).timestamp())
    highest_allowed_score = TimeseriesStorage.score_from_timestamp((datetime.today() + timedelta(days=1)).timestamp())

    for price_history_key in database.keys("*PriceVolumeHistoryStorage*"):
        # remove anything without a valid score (valid is between jan_1_2017 and today using timeseries score)
        database.zremrangebyscore(price_history_key, 0, old_score)
        database.zremrangebyscore(price_history_key, highest_allowed_score, datetime.today().timestamp())
    #PriceVolumeHistoryStorage



    # PriceStorage
    # delete all values 200 days old or older
    if STAGE:
        old_for_price_timestamp = now_timestamp - (5 * SMA_LIST[-1])  # 200 periods on short
    else:
        old_for_price_timestamp = now_timestamp - (3600 * 24 * SMA_LIST[-1])  # 200 days

    from apps.TA.storages.data.price import PriceStorage
    old_score = PriceStorage.score_from_timestamp(old_for_price_timestamp)

    price_history_keys = database.keys(f'*:PriceStorage:*')
    for price_history_key in price_history_keys:
        try:
            database.zremrangebyscore(price_history_key, 0, old_score)
        except Exception as e:
            logger.error(str(e))

    if STAGE:
        # remove all poloniex and bittrex data for now
        # todo: remove this and make sure it's not necessary
        for key in database.keys("*:poloniex:*"):
            database.delete(key)
        for key in database.keys("*:bittrex:*"):
            database.delete(key)

# from apps.TA.storages.data.memory_cleaner import redisCleanup as rC

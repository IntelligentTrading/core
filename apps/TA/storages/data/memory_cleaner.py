import logging
import time

from settings.redis_db import database

logger = logging.getLogger(__name__)


def redisCleanup():

    logger.info("I'M CLEANING REDIS !!!")

    do_not_disturb = bool(int(database.get("working on old stuff").decode("utf-8")))
    if do_not_disturb:
        return


    now_timestamp = int(time.time())

    # PriceVolumeHistoryStorage
    # delete all values 2 hours old or older
    old_for_pv_history = now_timestamp - (3600*2)

    pv_history_keys = database.keys(f'*:PriceVolumeHistoryStorage:*')
    for pv_history_key in pv_history_keys:
        try:
            database.zremrangebyscore(pv_history_key, 0, old_for_pv_history)
        except Exception as e:
            logger.error(str(e))


    # PriceStorage
    # delete all values 200 days old or older
    old_for_price_history = now_timestamp - (3600*24*200)

    price_history_keys = database.keys(f'*:PriceStorage:*')
    for price_history_key in price_history_keys:
        try:
            database.zremrangebyscore(price_history_key, 0, old_for_price_history)
        except Exception as e:
            logger.error(str(e))



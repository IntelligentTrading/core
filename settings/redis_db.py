import os
import logging
import redis
from apps.TA import deployment_type
from settings import DEBUG

SIMULATED_ENV = deployment_type == "LOCAL"
# todo: use this to mark keys in redis db, so they can be separated and deleted

logger = logging.getLogger('redis_db')

if deployment_type == "LOCAL":
    from settings.local_settings import TA_REDIS_URL
    if TA_REDIS_URL:
        database = redis.from_url(TA_REDIS_URL)
    else:
        REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
        database = redis.Redis(connection_pool=pool)
else:
    database = redis.from_url(os.environ.get("TA_REDIS_URL"))

if DEBUG:
    logger.info("Redis connection established for app database.")
    used_memory, maxmemory = int(database.info()['used_memory']), int(database.info()['maxmemory'])
    maxmemory_human = database.info()['maxmemory_human']
    logger.info(f"Redis currently consumes {round(100*used_memory/maxmemory if maxmemory != 0 else 0, 2)}% out of {maxmemory_human}")


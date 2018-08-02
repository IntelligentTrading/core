import os
import logging
import redis
from apps.TA import deployment_type


SIMULATED_ENV = deployment_type == "LOCAL"
# todo: use this to mark keys in redis db, so they can be separated and deleted

logger = logging.getLogger('redis_db')

if deployment_type == "LOCAL":
    REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    database = redis.Redis(connection_pool=pool)
else:
    database = redis.from_url(os.environ.get("REDIS_URL"))

logger.info("Redis connection established for app database.")

# hold this in python memory for fast access
# todo: does this even work with namespaces??
set_of_known_sets_in_redis = set()

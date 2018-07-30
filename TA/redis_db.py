import os
import logging
import redis
from TA import deployment_type


SIMULATED_ENV = deployment_type == "LOCAL"
# todo: use this to mark keys in redis db, so they can be separated and deleted

logger = logging.getLogger('redis_db')

REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
# todo: change db=1,2,3 for stage/prod/test envs?

database = redis.Redis(connection_pool=pool)
logger.info("Redis connection established for app database.")

# hold this in python memory for fast access
# todo: does this even work with namespaces??
set_of_known_sets_in_redis = set()

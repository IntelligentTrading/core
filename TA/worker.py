import os
import logging
import time
import redis


deployment_type = os.environ.get('DEPLOYMENT_TYPE', 'LOCAL')
if deployment_type == 'LOCAL':
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('flask_worker')


class WorkerException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)

#
# SIMULATED_ENV = os.get("env", "TEMP")
# todo: use this to mark keys in redis db, so they can be separated and deleted
#
REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
# todo: change db=1,2,3 for stage/prod/test envs?
redis_client = redis.Redis(connection_pool=pool)
logger.info("Redis connection established for worker redis_client.")


def work():

    from TA.storages.data.price import PriceSubscriber
    subscriber_classes = [
        PriceSubscriber,
    ]

    subscribers = {}
    for subscriber_class in subscriber_classes:
        subscribers[subscriber_class.__name__] = subscriber_class()

    logger.info("Pubsub clients are ready.")

    while True:
        for subscriber in subscribers:
            subscriber()
            time.sleep(0.001)  # be nice to the system :)

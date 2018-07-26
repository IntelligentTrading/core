import os
import logging
import time

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import redis

from TA.storages.data.price import DataSubscriber

logger = logging.getLogger('flask_worker')
logger.setLevel(logging.DEBUG)


class WorkerException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)


# SIMULATED_ENV = os.get("env", "TEMP")
# todo: use this to mark keys in redis db, so they can be separated and deleted

REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
# todo: change db=1,2,3 for stage/prod/test envs?

redis_client = redis.Redis(connection_pool=pool)
logger.info("Redis connection established.")


def main():
    subscribers = set()
    subscriber_classes = [DataSubscriber]

    for subscriber_class in subscriber_classes:
        subscribers.add(subscriber_class())

    logger.info("Pubsub clients are ready.")

    while True:
        for subscriber in subscribers:
            subscriber()
            time.sleep(0.001)  # be nice to the system :)

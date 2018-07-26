import os
import logging
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import redis

logger = logging.getLogger('flask_worker')
logger.setLevel(logging.DEBUG)


# SIMULATED_ENV = os.get("env", "TEMP")
# todo: use this to mark keys in redis db, so they can be separated and deleted

REDIS_HOST, REDIS_PORT = "127.0.0.1:6379".split(":")

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
# todo: change db=1,2,3 for stage/prod/test envs?

redis_client = redis.Redis(connection_pool=pool)
logger.info("Redis connection established.")

subscribers = [("function", "channel_name"), ("function", "channel_name")]

pubsub_clients = []

for function, channels in subscribers:

    pubsub_clients[function] = redis_client.pubsub()
    for channel in channels:
        pubsub_clients[function].subscribe(channel)

logger.info("Pubsub clients are ready.")

while True:
    for function, channels in subscribers:
        message = pubsub_clients[function].get_message()
        if not message:
            continue

        # example:
        # {
        #   'type': 'message',
        #   'pattern': None,
        #   'channel': b'channel',
        #   'data': b"dude, what's up?"
        # }
        try:
            if message['type'] == 'message':
                message['data']

        except KeyError: #message not in expected format. just ignore
            pass

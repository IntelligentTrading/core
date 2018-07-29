import os
import time
import redis
from TA import logger


# SIMULATED_ENV = os.get("env", "TEMP")
# todo: use this to mark keys in redis db, so they can be separated and deleted


def work():

    from TA.storages.data.price import PriceSubscriber
    subscriber_classes = [
        PriceSubscriber,
    ]

    subscribers = {}
    for subscriber_class in subscriber_classes:
        subscribers[subscriber_class.__name__] = subscriber_class()
        logger.debug(f'added subscriber {subscriber_class}')
        logger.debug(f'new subscriber is {subscribers[subscriber_class.__name__]}')

    logger.info("Pubsub clients are ready.")

    while True:
        for subscriber_name, subscriber_object in subscribers.items():
            subscriber_object()
            time.sleep(0.001)  # be nice to the system :)

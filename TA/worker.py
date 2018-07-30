import os
import time
import redis
from TA import logger, deployment_type


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

    for s in subscribers:
        logger.debug(f'latest channels: {subscribers[s].database.pubsub_channels()}')
        break


    logger.info("Pubsub clients are ready.")

    while True:
        for class_name in subscribers:
            logger.debug(f'checking subscription {class_name}: {subscribers[class_name]}')
            subscribers[class_name]()
            # print(subscribers[class_name].pubsub.get_message())
            # print(subscribers[class_name].database.pubsub_channels())
            # print(subscribers[class_name].database)
            # time.sleep(5)  # be nice to the system :)
            time.sleep(0.001)  # be nice to the system :)

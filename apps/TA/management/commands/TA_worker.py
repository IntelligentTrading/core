import time
import logging
import random
from django.core.management.base import BaseCommand

from apps.TA.storages.data.memory_cleaner import redisCleanup
from apps.TA.indicators.overlap import sma, ema, wma, dema, tema, trima, bbands, ht_trendline, kama, midprice
from apps.TA.indicators.momentum import rsi

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Redis Subscribers for TA'

    def handle(self, *args, **options):
        logger.info("Starting TA worker.")

        from apps.TA.storages.data.price import PriceSubscriber
        subscriber_classes = [
            PriceSubscriber,
            # VolumeSubscriber,

            # OVERLAP INDICATORS
            midprice.MidpriceSubscriber,
            sma.SmaSubscriber, ema.EmaSubscriber, wma.WmaSubscriber,
            dema.DemaSubscriber, tema.TemaSubscriber, trima.TrimaSubscriber, kama.KamaSubscriber,
            bbands.BbandsSubscriber, ht_trendline.HtTrendlineSubscriber,

            # MOMENTUM INDICATORS
            rsi.RsiSubscriber,
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
                # logger.debug(f'checking subscription {class_name}: {subscribers[class_name]}')
                try:
                    subscribers[class_name]()  # run subscriber class
                except Exception as e:
                    logger.error(str(e))
                # print(subscribers[class_name].pubsub.get_message())
                # print(subscribers[class_name].database.pubsub_channels())
                # print(subscribers[class_name].database)
                # time.sleep(5)  # be nice to the system :)
                time.sleep(0.001)  # be nice to the system :)

                if bool(random.randrange(10**8) % (10**6) == 0):
                    redisCleanup()

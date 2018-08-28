import time
import logging
import random
from django.core.management.base import BaseCommand

from apps.TA.storages.data.memory_cleaner import redisCleanup
from apps.TA.indicators.overlap import sma, ema, wma, dema, tema, trima, bbands, ht_trendline, kama, midprice
from apps.TA.indicators.momentum import adx, adxr, apo, aroon, aroonosc, bop, cci, cmo, dx, macd, mfi, mom, ppo, roc, rocr, rsi, stoch, stochf, stochrsi, trix, ultosc, willr
from settings import LOCAL
from settings.redis_db import database

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
            adx.AdxSubscriber, adxr.AdxrSubscriber, apo.ApoSubscriber, aroon.AroonSubscriber, aroonosc.AroonOscSubscriber,
            bop.BopSubscriber, cci.CciSubscriber, cmo.CmoSubscriber, dx.DxSubscriber, macd.MacdSubscriber,
            # mfi.MfiSubscriber,
            mom.MomSubscriber, ppo.PpoSubscriber, roc.RocSubscriber, rocr.RocrSubscriber, rsi.RsiSubscriber,
            stoch.StochSubscriber, stochf.StochfSubscriber, stochrsi.StochrsiSubscriber,
            trix.TrixSubscriber, ultosc.UltoscSubscriber, willr.WillrSubscriber,

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
            counter = 0
            for class_name in subscribers:
                # logger.debug(f'checking subscription {class_name}: {subscribers[class_name]}')
                try:
                    subscribers[class_name]()  # run subscriber class
                except Exception as e:
                    logger.error(str(e))
                # print(subscribers[class_name].pubsub.get_message())
                # print(subscribers[class_name].database.pubsub_channels())
                # print(subscribers[class_name].database)
                time.sleep(0.0001)  # be nice to the system :)

                if counter > (3600 / 0.0001):
                    counter = 0
                    try:
                        if int(database.info()['used_memory']) > (2 ** 30 * .9):
                            redisCleanup()
                    except:
                        pass
                else:
                    counter += 1

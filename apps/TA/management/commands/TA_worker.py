import logging
import time

from django.core.management.base import BaseCommand

from apps.TA.storages.data.memory_cleaner import redisCleanup
from settings.rabbitmq import WorkQueue
from settings.redis_db import database

logger = logging.getLogger(__name__)

earliest_price_timestamp = int(float(database.zrangebyscore("BTC_USDT:bittrex:PriceStorage:close_price", 0, "inf", 0, 1)[0].decode("utf-8").split(":")[0]))


# todo for making this more efficient
#  - only 5min price history, all else can be generated on demand
# ✅ def compress(timestamp): return (timestamp - JAN_1_2017_TIMESTAMP)/300
#  - floor all prices to 6 sig-figs (saving up to 6 digits for XX_USDT prices) on TickerStorage
# ✅  - but maybe no because we like operating with satoshis always
# ✅ - cast scores on indicators to integers (saving 2 digits)
# ✅ - use rabbitmq as a centralized task queue so workers can scale horizontally
#  - reduce number of tickers being processed


class Command(BaseCommand):
    help = 'Run Redis Subscribers for TA'

    def handle(self, *args, **options):
        logger.info("Starting TA worker.")

        subscribers = {}
        for subscriber_class in get_subscriber_classes():
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


    def new_handle(self, *args, **options):
        topics = [subscriber_class.class_describer for subscriber_class in get_subscriber_classes()]

        work_queues = []
        for topic in set(topics):
            work_queues.append(WorkQueue(topic=topic))
        for queue in work_queues:
            queue.process_tasks_async()

        while True:
            time.sleep(5)  # wait for the world to end


def get_subscriber_classes():

    from apps.TA.storages.data.price import PriceSubscriber
    from apps.TA.indicators.overlap import sma, ema, wma, dema, tema, trima, bbands, ht_trendline, kama, midprice
    from apps.TA.indicators.momentum import adx, adxr, apo, aroon, aroonosc, bop, cci, cmo, dx, macd, mom, ppo, \
        roc, rocr, rsi, stoch, stochf, stochrsi, trix, ultosc, willr

    return [
        PriceSubscriber,
        # todo: VolumeSubscriber,

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

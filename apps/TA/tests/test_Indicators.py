import time
import logging
import numpy as np
from django.test import TestCase

from apps.TA import JAN_1_2017_TIMESTAMP, PERIODS_24HR
from apps.TA.storages.data.price import PriceStorage
from apps.TA.storages.data.pv_history import default_price_indexes
from settings.redis_db import database

logger = logging.getLogger(__name__)

ticker = "CWC_ETH"
exchange = "binance"


class IndicatorTestClass(object):

    storage_class = None
    subscriber_class = None


    def setUp(self):
        max_periods = PERIODS_24HR  # * 200

        prices = {
            # 'close_volume': np.random.random(max_periods)
            'high_price': np.random.random(max_periods),
            'low_price': np.random.random(max_periods),
            'open_price': np.random.random(max_periods),
            'close_price': np.random.random(max_periods),
        }

        timestamp = JAN_1_2017_TIMESTAMP

        price_storage = PriceStorage(ticker=ticker,
                                     exchange=exchange,
                                     timestamp=timestamp)

        for index in default_price_indexes:
            price_storage.index = index

            for price in prices[index]:
                timestamp += 300

                price_storage.unix_timestamp = timestamp
                price_storage.value = price
                price_storage.save()

                self.last_price_storage = price_storage

    def test_subscriber(self):

        subscriber = self.subscriber_class()
        subscriber()
        self.last_price_storage.save()
        subscriber()
        subscriber()

        time.sleep(1)

        key_substring = f"{ticker}:{exchange}:{self.storage_class.__name__}"
        logger.info("looking for keys like " + key_substring)

        keys = database.keys(f"*{key_substring}*")
        assert len(keys)

        for key in keys:
            assert len(
                database.zrange(key,
                    self.last_price_storage.unix_timestamp,
                    self.last_price_storage.unix_timestamp)
            )

            # assert len(self.storage_class.query(
            #     ticker=ticker,
            #     exchange=exchange,
            #     timestamp=self.last_price_storage.unix_timestamp,
            # )['values'])





    def tearDown(self):
        for key in database.keys(f"*:{ticker}:*"):
            database.delete(key)


from apps.TA.indicators.overlap import sma

class SmaTestCase(IndicatorTestClass, TestCase):
    storage_class = sma.SmaStorage
    subscriber_class = sma.SmaSubscriber

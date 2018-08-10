import time

from django.test import TestCase

from apps.TA import JAN_1_2017_TIMESTAMP
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, PriceVolumeHistoryException

ticker1 = "TOM_BTC"
ticker2 = "CWC_ETH"

timestamp = int(time.time())
old_timestamp = timestamp - (200 * 24 * 3600)  # 200 days
index = "close_price"
value = 123456

exchange = "binance"

class PriceHistoryTestCase(TestCase):
    def setUp(self):

        self.price_history = PriceVolumeHistoryStorage(
            ticker=ticker1, exchange=exchange, timestamp=timestamp,
            index=index, value=value
        )

    def test_must_use_standard_index(self):
        """Animals that can speak are correctly identified"""
        self.price_history.index = "some_other_price"

        self.assertRaises(
            PriceVolumeHistoryException,
            self.price_history.save()
        )

    def test_old_timestamp_raises_exception(self):
        self.price_history.unix_timestamp = JAN_1_2017_TIMESTAMP - 1
        self.assertRaises(
            PriceVolumeHistoryException,
            self.price_history.save()
        )

    def test_dublicate_returns_0(self):
        self.price_history.index = "close_price"
        self.price_history.value = 12345
        self.price_history.unix_timestamp = JAN_1_2017_TIMESTAMP + 298343

        # first time saves, returns 1 for 1 entry added
        self.assertEqual(self.price_history.save(), 1)
        # second time saves, returns 0 for duplicate, no entry added
        self.assertEqual(self.price_history.save(), 0)

    def test_query_tolerance(self):
        query_results = PriceVolumeHistoryStorage.query(ticker=ticker1, exchange=exchange,
                                            index=index, timestamp=timestamp,
                                            periods_range=1, timestamp_tolerance=29)
        self.assertLess(len(query_results['values']), 7)



    def tearDown(self):
        from settings.redis_db import database
        database.delete(self.price_history.get_db_key())




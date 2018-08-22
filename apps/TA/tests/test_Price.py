import time

from django.test import TestCase

from apps.TA import JAN_1_2017_TIMESTAMP
from apps.TA.storages.abstract.timeseries_storage import TimeseriesException
from apps.TA.storages.data.price import PriceStorage, PriceException
from apps.TA.storages.data.pv_history import PriceVolumeHistoryException


ticker1 = "TOM_BTC"
ticker2 = "CWC_ETH"

timestamp = (int(time.time()) // 300) * 300
old_timestamp = timestamp - (200 * 24 * 3600)  # 200 days
index = "close_price"
value = 123456

exchange = "binance"


class PriceTestCase(TestCase):
    def setUp(self):
        self.price = PriceStorage(
            ticker=ticker1, exchange=exchange, timestamp=timestamp,
            index=index, value=value
        )

    def test_must_use_standard_index(self):
        self.price.index = "some_other_price"

        self.assertRaises(
            PriceException,
            self.price.save
        )

    def test_old_timestamp_raises_exception(self):
        def instantiate_old_price():
            old_price = PriceStorage(
                ticker=ticker1, exchange=exchange,
                timestamp=JAN_1_2017_TIMESTAMP - 300,  # too old
                index=index, value=value
            )

        self.assertRaises(
            TimeseriesException,
            instantiate_old_price
        )

    def test_duplicate_returns_0(self):
        self.price.index = index
        self.price.value = value
        self.price.unix_timestamp = JAN_1_2017_TIMESTAMP + 300

        # first time saves, returns 1 for 1 entry added
        self.assertEqual(self.price.save(), 1)
        # second time saves, returns 0 for duplicate, no entry added
        self.assertEqual(self.price.save(), 0)

    def test_cleanup_old_values(self):
        self.price.unix_timestamp = old_timestamp
        self.price.save()
        time.sleep(2)
        self.price.unix_timestamp = timestamp
        self.price.save()
        time.sleep(2)
        query_results = self.price.query(timestamp=old_timestamp,
                                                 index=index,
                                                 exchange=self.price.exchange,
                                                 ticker=self.price.ticker)

        self.assertEqual(
            int(query_results['values'][-1]),
            value)



    def tearDown(self):
        from settings.redis_db import database
        database.delete(self.price.get_db_key())


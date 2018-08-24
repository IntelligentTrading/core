import time

from django.test import TestCase

from apps.TA import JAN_1_2017_TIMESTAMP
from apps.TA.indicators import SmaStorage

ticker1 = "TOM_BTC"
ticker2 = "CWC_ETH"

timestamp = (int(time.time()) // 300) * 300
old_timestamp = timestamp - (200 * 24 * 3600)  # 200 days
value = 123456
periods = 20
exchange = "binance"


class SmaTestCase(TestCase):
    def setUp(self):
        self.sma = SmaStorage(
            ticker=ticker1, exchange=exchange, timestamp=timestamp,
            value=value, periods=periods
        )

    def test_duplicate_returns_0(self):
        self.sma.value = value
        self.sma.unix_timestamp = JAN_1_2017_TIMESTAMP + 300

        # first time saves, returns 1 for 1 entry added
        self.assertEqual(self.sma.save(), 1)
        # second time saves, returns 0 for duplicate, no entry added
        self.assertEqual(self.sma.save(), 0)

    def test_does_not_cleanup_old_values(self):
        self.sma.unix_timestamp = old_timestamp
        self.sma.save()
        time.sleep(2)
        self.sma.unix_timestamp = timestamp
        self.sma.save()
        time.sleep(2)
        query_results = self.sma.query(timestamp=old_timestamp,
                                       periods_key=periods,
                                       exchange=exchange,
                                       ticker=ticker1)

        self.assertEqual(
            int(query_results['values'][-1]),
            value)


    def tearDown(self):
        from settings.redis_db import database
        database.delete(self.sma.get_db_key())


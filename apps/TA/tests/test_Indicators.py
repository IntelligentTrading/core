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


class IndicatorsTestCase(TestCase):

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

    def run_subscriber(self, storage_class, subscriber_class):

        subscriber = subscriber_class()
        subscriber()
        self.last_price_storage.save(publish=True)
        subscriber()
        subscriber()

        time.sleep(0.1)

        key_substring = f"{ticker}:{exchange}:{storage_class.__name__}"
        logger.info("looking for keys like " + key_substring)

        keys = database.keys(f"*{key_substring}*")
        assert len(keys)

        for key in keys:
            assert len(
                database.zrangebyscore(key,
                    self.last_price_storage.unix_timestamp,
                    self.last_price_storage.unix_timestamp)
            )

            # assert len(storage_class.query(
            #     ticker=ticker,
            #     exchange=exchange,
            #     timestamp=self.last_price_storage.unix_timestamp,
            # )['values'])


    # OVERLAP INDICATORS

    def test_sma(self):
        from apps.TA.indicators.overlap.sma import SmaStorage, SmaSubscriber
        self.run_subscriber(SmaStorage, SmaSubscriber)

    def test_ema(self):
        from apps.TA.indicators.overlap.ema import EmaStorage, EmaSubscriber
        self.run_subscriber(EmaStorage, EmaSubscriber)

    def test_wma(self):
        from apps.TA.indicators.overlap.wma import WmaStorage, WmaSubscriber
        self.run_subscriber(WmaStorage, WmaSubscriber)

    def test_dema(self):
        from apps.TA.indicators.overlap.dema import DemaStorage, DemaSubscriber
        self.run_subscriber(DemaStorage, DemaSubscriber)

    def test_tema(self):
        from apps.TA.indicators.overlap.tema import TemaStorage, TemaSubscriber
        self.run_subscriber(TemaStorage, TemaSubscriber)

    def test_trima(self):
        from apps.TA.indicators.overlap.trima import TrimaStorage, TrimaSubscriber
        self.run_subscriber(TrimaStorage, TrimaSubscriber)

    def test_bbands(self):
        from apps.TA.indicators.overlap.bbands import BbandsStorage, BbandsSubscriber
        self.run_subscriber(BbandsStorage, BbandsSubscriber)

    def test_ht_trendline(self):
        from apps.TA.indicators.overlap.ht_trendline import HtTrendlineStorage, HtTrendlineSubscriber
        self.run_subscriber(HtTrendlineStorage, HtTrendlineSubscriber)

    # MOMENTUM INDICATORS

    def test_adx(self):
        from apps.TA.indicators.momentum.adx import AdxStorage, AdxSubscriber
        self.run_subscriber(AdxStorage, AdxSubscriber)

    def test_adxr(self):
        from apps.TA.indicators.momentum.adxr import AdxrStorage, AdxrSubscriber
        self.run_subscriber(AdxrStorage, AdxrSubscriber)

    def test_apo(self):
        from apps.TA.indicators.momentum.apo import ApoStorage, ApoSubscriber
        self.run_subscriber(ApoStorage, ApoSubscriber)

    def test_aroon(self):
        from apps.TA.indicators.momentum.aroon import AroonStorage, AroonSubscriber
        self.run_subscriber(AroonStorage, AroonSubscriber)

    def test_aroonosc(self):
        from apps.TA.indicators.momentum.aroonosc import AroonOscStorage, AroonOscSubscriber
        self.run_subscriber(AroonOscStorage, AroonOscSubscriber)

    def test_bop(self):
        from apps.TA.indicators.momentum.bop import BopStorage, BopSubscriber
        self.run_subscriber(BopStorage, BopSubscriber)

    def test_rsi(self):
        from apps.TA.indicators.momentum.rsi import RsiStorage, RsiSubscriber
        self.run_subscriber(RsiStorage, RsiSubscriber)


    # END INDICATORS

    def tearDown(self):
        for key in database.keys(f"*:{ticker}:*"):
            database.delete(key)

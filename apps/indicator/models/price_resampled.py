import pandas as pd
import numpy as np
#import talib.stream as tas
import logging

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from datetime import timedelta, datetime
from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models.abstract_indicator import AbstractIndicator

from apps.signal.models import Signal

# TODO: declare it better
horizons = {15: "short", 60: "medium", 360: "long"}
time_speed = 1  # set to 1 for production, 10 for fast debugging

logger = logging.getLogger(__name__)

class PriceResampled(AbstractIndicator):
    # source inherited from AbstractIndicator
    # coin inherited from AbstractIndicator
    # timestamp inherited from AbstractIndicator

    period = models.PositiveSmallIntegerField(null=False, default=15)  # minutes (eg. 15)

    mean_price_satoshis = models.IntegerField(null=True) # price_satoshis
    min_price_satoshis = models.IntegerField(null=True) # price_satoshis
    max_price_satoshis = models.IntegerField(null=True) # price_satoshis

    SMA50_satoshis = models.IntegerField(null=True) # price_satoshis
    SMA200_satoshis = models.IntegerField(null=True) # price_satoshis

    EMA50_satoshis = models.IntegerField(null=True) # price_satoshis
    EMA200_satoshis = models.IntegerField(null=True) # price_satoshis

    relative_strength = models.FloatField(null=True) # relative strength
    # RSI = relative strength index, see property

    _resampled_price_ts = None

    # MODEL PROPERTIES

    @property
    def relative_strength_index(self): # relative strength index
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))


    # MODEL FUNCTIONS
    def get_price_ts(self):
        '''
        Caches from DB the nessesary amount of records to calculate SMA, EMA etc
        :return: pd.Series of last 200 time points
        '''
        if self._resampled_price_ts is None:
            back_in_time_records = list(PriceResampled.objects.filter(
                period=self.period,
                coin=self.coin,
                timestamp__gte = datetime.now() - timedelta(minutes=(self.period*200+50)) # 50 is for safety
            ).values('mean_price_satoshis'))

            if not back_in_time_records:
                return None

            self._resampled_price_ts = pd.Series([rec['mean_price_satoshis'] for rec in back_in_time_records])
            # TALIB: price_ts_nd = np.array([ rec['mean_price_satoshis'] for rec in raw_data])

        return self._resampled_price_ts


    def calc_SMA(self):
        price_ts = self.get_price_ts()

        if price_ts is not None:  # if we have at least one timepoint (to avoid ta-lib SMA error, not nessesary for pandas)
            # calculate SMA and save it in the same record
            # TALIB: price_ts_nd = np.array([ rec['mean_price_satoshis'] for rec in raw_data])
            SMA50 = price_ts.rolling(window=int(50/time_speed), center=False, min_periods=4).mean()
            SMA50 = float(SMA50.tail(1))
            SMA200 = price_ts.rolling(window=int(200/time_speed), center=False, min_periods=4).mean()
            SMA200 = float(SMA200.tail(1))

            # TALIB:_SMA50 = tas.SMA(price_ts_nd.astype(float), timeperiod=50/time_speed)
            # TALIB:_MA200 = tas.SMA(price_ts_nd.astype(float), timeperiod=200/time_speed)

            if not np.isnan(SMA50): self.SMA50_satoshis = SMA50
            if not np.isnan(SMA200): self.SMA200_satoshis = SMA200


    def calc_EMA(self):
        price_ts = self.get_price_ts()

        # alpha is a decay constant which tells how much back in time
        # the decay make the contribution of the time point negledgibly small
        alpha50 = 2.0 / (50+1)
        alpha200 = 2.0 / (200 + 1)

        if price_ts is not None:
            EMA50 = price_ts.ewm(alpha=alpha50, min_periods=5).mean()
            EMA50 = float(EMA50.tail(1))
            EMA200 = price_ts.ewm(alpha=alpha200, min_periods=5).mean()
            EMA200 = float(EMA200.tail(1))

            if not np.isnan(EMA50): self.EMA50_satoshis = EMA50
            if not np.isnan(EMA200): self.EMA200_satoshis = EMA200



    def check_signal(self):

        # DB records for the last two time points
        last_two_rows = list(
            PriceResampled.objects.
                filter(period=self.period, coin=self.coin).
                order_by('-timestamp').
                values('mean_price_satoshis', 'SMA50_satoshis','SMA200_satoshis','EMA50_satoshis','EMA200_satoshis'))[0:2]

        # TODO: do it better! skip the currency if there is no information about this currency
        if not last_two_rows:
            logger.debug('----------> EMIT skipped')
            exit()

        prices = np.array([row['mean_price_satoshis'] for row in last_two_rows])

        # List of all indicators to calculate signals
        metrics = [
            {'low':'SMA50_satoshis', 'high':'SMA200_satoshis', 'name':'SMA'},
            {'low':'EMA50_satoshis', 'high':'EMA200_satoshis', 'name':'EMA'}
        ]

        # iterate through all metrics which might generate signals, SMA, EMA etc
        for metr in metrics:
            m_low = np.array([row[metr['low']] for row in last_two_rows])
            m_high = np.array([row[metr['high']] for row in last_two_rows])

            # check for ind_A signal
            if all(prices != None) and all(m_low != None):
                ind_A = np.sign(prices - m_low)
                if ind_A[0] == 0:
                    logger.debug('Indicator (price-low) did not change since last time, canot emit the signal' +
                                 str(prices) + str(m_low))

                if np.sum(ind_A) == 0 and any(ind_A) != 0:  # emit a signal if indicator changes its sign
                    logger.debug("Ind_A difference:" +str(ind_A))
                    signal_A = Signal(
                        coin=self.coin,
                        signal=metr['name'],
                        trend=int(ind_A[0]),
                        horizon=horizons[self.period],
                        strength_value=int(1),
                        strength_max=int(3)

                    )
                    signal_A.print()
                    signal_A.send()

            if all(prices != None) and all(m_high != None):
                ind_B = np.sign(prices - m_high)
                if ind_B[0] == 0:
                    logger.debug('Indicator (price-high) did not change since last time, canot emit the signal' +
                                 str(prices) + str(m_high))

                if np.sum(ind_B) == 0 and any(ind_B) != 0:
                    logger.debug("Ind_B difference:" + str(ind_B))
                    signal_B = Signal(
                        coin=self.coin,
                        signal=metr['name'],
                        trend=int(ind_B[0]),
                        horizon=horizons[self.period],
                        strength_value=int(2),
                        strength_max=int(3)

                    )
                    signal_B.print()
                    signal_B.send()

            if all(m_high != None) and all(m_low != None) and all(m_high != None):
                ind_C = np.sign(m_low - m_high)
                if ind_C[0] == 0:
                    logger.debug('Indicator (low-high) did not change since last time, canot emit the signal' +
                                 str(m_low) + str(m_high))

                if np.sum(ind_C) == 0 and any(ind_C) != 0:
                    logger.debug("Ind_C difference:" + str(ind_C))
                    signal_C = Signal(
                        coin=self.coin,
                        signal=metr['name'],
                        trend=int(ind_C[0]),
                        horizon=horizons[self.period],
                        strength_value=int(3),
                        strength_max=int(3)

                    )
                    signal_C.print()
                    signal_C.send()

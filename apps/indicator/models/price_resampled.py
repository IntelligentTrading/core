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
from apps.user.models.user import get_horizon_value_from_string

from settings import HORIZONS   # mapping from bin size to a name short/medium
from settings import time_speed # speed of the resampling, 10 for fast debug, 1 for prod

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
    # rsi = 100 - 100 / (1 + rUp / rDown)
    def relative_strength_index(self): # relative strength index
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))


    # MODEL FUNCTIONS
    def get_price_ts(self):
        '''
        Caches from DB the min nessesary amount of records to calculate SMA, EMA etc
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
        # period= 15,60,360, this ts is already reflects one of those before we call it
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

            if not np.isnan(SMA50):
                self.SMA50_satoshis = SMA50
            if not np.isnan(SMA200):
                self.SMA200_satoshis = SMA200


    def calc_EMA(self):
        price_ts = self.get_price_ts()

        # alpha is a decay constant which tells how much back in time
        # the decay make the contribution of the time point negledgibly small
        alpha50 = 2.0 / (50+1)
        alpha200 = 2.0 / (200 + 1)

        if price_ts is not None:
            EMA50 = price_ts.ewm(alpha=alpha50, min_periods=5).mean()
            EMA50 = float(EMA50.tail(1))  # get the last value for "now" time point
            EMA200 = price_ts.ewm(alpha=alpha200, min_periods=5).mean()
            EMA200 = float(EMA200.tail(1))

            if not np.isnan(EMA50):
                self.EMA50_satoshis = EMA50
            if not np.isnan(EMA200):
                self.EMA200_satoshis = EMA200


    def calc_RS(self):
        '''
        Relative Strength calculation.
        The RSI is calculated a a property, we only save RS
        (RSI is a momentum oscillator that measures the speed and change of price movements.)
        :return:
        '''

        # get Series of last 200 time points
        # period= 15,60,360, this ts is already reflects one of those before we call it
        price_ts = self.get_price_ts()

        # difference btw start and close of the day, remove the first NA
        delta = price_ts.diff()
        delta = delta[1:]

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the 14 period back EWMA for each up/down trends
        # QUESTION: shall this 14 perid depends on period 15,60, 360?

        roll_up = up.ewm(com = 14, min_periods=3).mean()
        roll_down = np.abs(down.ewm(com = 14, min_periods=3).mean())

        rs_ts = roll_up / roll_down

        self.relative_strength = float(rs_ts.tail(1))  # get the last element for the last time point


    def check_cross_over_signal(self):
        """
        Check and emit cross over SMA (EMA) signals to SQS
        :return:
        """

        # List of all indicators to calculate signals
        INDICATORS = [
            {'low':'SMA50_satoshis', 'high':'SMA200_satoshis', 'name':'SMA'}
        ]

        #INDICATORS = [
        #    {'low':'SMA50_satoshis', 'high':'SMA200_satoshis', 'name':'SMA'},
        #    {'low':'EMA50_satoshis', 'high':'EMA200_satoshis', 'name':'EMA'}
        #]

        # get DB records for the last two time points
        last_two_rows = list(
            PriceResampled.objects.
                filter(period=self.period, coin=self.coin).
                order_by('-timestamp').
                values('mean_price_satoshis', 'SMA50_satoshis','SMA200_satoshis','EMA50_satoshis','EMA200_satoshis'))[0:2]

        # Sanity check:
        if not last_two_rows:
            logger.debug('Signal skipped: There is no information in DB about ' + str(self.coin) + str(self.period))
            exit()

        prices = np.array([row['mean_price_satoshis'] for row in last_two_rows])
        if any(prices) is None: exit()

        # check and emit SMA, EMA signals
        # iterate through all metrics which might generate signals, SMA, EMA etc

        for ind in INDICATORS:   # only for SMA for now
            # get last two time points from indicators ( SMA20, SMA200 etc)
            m_low  = np.array([row[ind['low']] for row in last_two_rows])
            m_high = np.array([row[ind['high']] for row in last_two_rows])

            horizon = get_horizon_value_from_string(display_string=HORIZONS[self.period])

            # ind A
            # trend = 0 if sign is not changed, -1 if bearish, +1 if bullish
            if all(m_low != None):  # now we know both the price and low exists
                ind_A_sign = np.sign(prices - m_low)  # [-1, 1]
                trend_A = int(ind_A_sign[0]) if np.prod(ind_A_sign) < 0 else 0   #if indicator changes its sign

            # ind B
            if all(m_high != None):
                ind_B_sign = np.sign(prices - m_high)
                trend_B = int(ind_B_sign[0]) if np.prod(ind_B_sign) < 0 else 0

            # ind C
            if all(m_high != None) and all(m_low != None):
                ind_C_sign = np.sign(m_low - m_high)
                trend_C = int(ind_C_sign[0]) if np.prod(ind_C_sign) < 0 else 0

            # implement
            #    if A is BEARISH ,  that's a weak signal
            #    if A and B are both BEARISH, that's a medium signal
            #    if A, B, and C are all BEARISH, that's a strong signal
            # and generate the signals if neccesary

            logger.debug("ind_A trend: " + str(trend_A))
            logger.debug("ind_B trend: " + str(trend_B))
            logger.debug("ind_C trend: " + str(trend_C))

            # emit signals
            if np.abs(trend_A + trend_B + trend_C) == 3:  # if A, B and C all have the same direction
                signal_strong = Signal(
                    coin=self.coin,
                    signal=ind['name'],  # SMA/ EMA
                    trend=trend_C,   # take any of A or B or C, since they hav the same sign
                    horizon=horizon,
                    strength_value=int(3),  # strong signal
                    strength_max=int(3),
                    timestamp=self.timestamp
                )
                signal_strong.save()  # saving will send immediately if not already sent
                signal_strong.print()
            elif (trend_A * trend_B) > 0:   # weak signal
                signal_medium = Signal(
                    coin=self.coin,
                    signal=ind['name'],  # SMA, EMA
                    trend=trend_B,  # take any of A or B, since they hav the same sign
                    horizon=horizon,
                    strength_value=int(2),  # medium signal
                    strength_max=int(3),
                    timestamp=self.timestamp
                )
                signal_medium.save()  # saving will send immediately if not already sent
                signal_medium.print()
            elif np.abs(trend_A) > 0: # weak signal
                signal_weak = Signal(
                    coin=self.coin,
                    signal=ind['name'],  # SMA, EMA
                    trend=trend_A,
                    horizon=horizon,
                    strength_value=int(1),  # weak signal
                    strength_max=int(3),
                    timestamp=self.timestamp
                )
                signal_weak.save()  # saving will send immediately if not already sent
                signal_weak.print()
            else:
                logger.debug(" no changes in trends, so No signals to generate ")


    # if they cross a certain level:
    # RSI below 30 = send signal
    # RSI above 75 = send signal

    # RSI 70-74 = overbought (weak signal) = 1
    # RSI 75-79 = overbought (medium signal) = 2
    # RSI 80+ = overbought (strong signal) = 3
    #
    # RSI 30-26 = oversold (medium signal) = -2
    # RSI 25-20- = oversold (strong signal) = -3

    def check_rsi_signal(self):
        horizon = get_horizon_value_from_string(display_string=HORIZONS[self.period])
        rsi_strength = 0
        rsi = self.relative_strength_index

        # emit signals if rsi is in a certain range
        if rsi >= 0 and rsi <= 100 :
            logger.debug("   RSI= " + str(rsi) + ', for period ' + str(self.period))
            if rsi >= 80:
                rsi_strength = 3  # Extremely overbought
            elif rsi >= 75:
                rsi_strength = 2  # very overbought
            elif rsi >= 70:
                rsi_strength = 1  # overbought
            elif rsi <= 20:
                rsi_strength = -3  # Extremely oversold
            elif rsi <= 25:
                rsi_strength = -2   # very oversold
            elif rsi <= 30:
                rsi_strength = -1  # oversold

            #did send same signal recently??
            previous_signal = Signal.objects.filter(
                coin=self.coin,
                signal='RSI',
                strength_value=np.abs(rsi_strength),
                trend=np.sign(rsi_strength),
                timestamp__gte=self.timestamp - timedelta(minutes=30)
            ).first()

            if rsi_strength != 0 and not previous_signal:
                signal_rsi = Signal(
                    coin=self.coin,
                    signal='RSI',
                    rsi_value=rsi,
                    trend=np.sign(rsi_strength),
                    horizon=horizon,
                    strength_value=np.abs(rsi_strength),
                    strength_max=int(3),
                    timestamp=self.timestamp
                )
                signal_rsi.save()  # saving will send immediately if not already sent
                signal_rsi.print()
        else:
            logger.error("RSI out of range!! ")



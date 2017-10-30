import pandas as pd
import numpy as np
#import talib.stream as tas
import logging

from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from datetime import timedelta
from apps.channel.models.exchange_data import SOURCE_CHOICES
from apps.indicator.models.abstract_indicator import AbstractIndicator

from apps.indicator.telegram_alert import TelegramAlert

# TODO: declare it better
horizons = {15: "short", 60: "medium", 360: "long"}
time_speed = 1  # set to 1 for production, 10 for fast debugging

logger = logging.getLogger(__name__)

class PriceResampled(AbstractIndicator):
    # source inherited from AbstractIndicator
    # coin inherited from AbstractIndicator
    # timestamp inherited from AbstractIndicator

    period = models.PositiveSmallIntegerField(null=False, default=15)  # minutes (eg. 15)

    mean_price_satoshis = models.IntegerField(null=True) # satoshis
    min_price_satoshis = models.IntegerField(null=True) # satoshis
    max_price_satoshis = models.IntegerField(null=True) # satoshis

    SMA50_satoshis = models.IntegerField(null=True) # satoshis
    SMA200_satoshis = models.IntegerField(null=True) # satoshis

    EMA50_satoshis = models.IntegerField(null=True) # satoshis
    EMA200_satoshis = models.IntegerField(null=True) # satoshis

    relative_strength = models.FloatField(null=True) # relative strength
    # RSI = relative strength index, see property


    # MODEL PROPERTIES

    @property
    def relative_strength_index(self): # relative strength index
        if self.relative_strength is not None:
            return 100.0 - (100.0 / (1.0 + self.relative_strength))


    # MODEL FUNCTIONS


    def calc_SMA(self):

        # get resampled data(period=10, coin="ETH")  for SMA calculation
        # TODO: need to limit data back in time.. otherwise in a year it might take too much time in memory...
        raw_data = list(PriceResampled.objects.filter(period=self.period, coin=self.coin).values('mean_price_satoshis'))

        if raw_data:  # if we have at least on bin (to avoid SMA error)
            # calculate SMA and save it in the same record
            price_ts_nd = np.array([ rec['mean_price_satoshis'] for rec in raw_data])
            price_ts = pd.Series([rec['mean_price_satoshis'] for rec in raw_data])

            SMA50 = price_ts.rolling(window=int(50/time_speed), center=False, min_periods=4).mean()
            SMA50 = float(SMA50.tail(1))
            SMA200 = price_ts.rolling(window=int(200/time_speed), center=False, min_periods=4).mean()
            SMA200 = float(SMA200.tail(1))

            #_SMA50 = tas.SMA(price_ts_nd.astype(float), timeperiod=50/time_speed)
            #_MA200 = tas.SMA(price_ts_nd.astype(float), timeperiod=200/time_speed)

            #print("talib  SMA50=" + str(_SMA50) + "  SMA200=" + str(_MA200))
            #print("pandas SMA50=" + str(SMA50) + "  SMA200=" + str(SMA200))

            if not np.isnan(SMA50): self.SMA50_satoshis = SMA50
            if not np.isnan(SMA200): self.SMA200_satoshis = SMA200


    def check_signal(self):
        # get the last
        last_two_rows = list(
            PriceResampled.objects.
                filter(period=self.period, coin=self.coin).
                order_by('-timestamp').
                values('mean_price_satoshis', 'SMA50_satoshis','SMA200_satoshis'))[0:2]

        # TODO: do it better! skip the currency if there is no information about this currency
        if not last_two_rows:
            logger.debug('----------> EMIT skipped')
            exit()

        prices = np.array([row['mean_price_satoshis'] for row in last_two_rows])
        SMA50s = np.array([row['SMA50_satoshis'] for row in last_two_rows])
        SMA200s = np.array([row['SMA200_satoshis'] for row in last_two_rows])

        # check for ind_A signal
        if all(prices != None) and all(SMA50s != None):
            ind_A = np.sign(prices - SMA50s)
            if ind_A[0] == 0:
                logger.debug(prices, SMA50s)

            if np.sum(ind_A) == 0 and any(ind_A) != 0:  # emit a signal if indicator changes its sign
                logger.debug("Ind_A difference:" +str(ind_A))
                alert_A = TelegramAlert(
                    coin=self.coin,
                    signal="SMA",
                    trend=int(ind_A[0]),
                    horizon=horizons[self.period],
                    strength_value=int(1),
                    strength_max=int(3)

                )
                alert_A.print()
                alert_A.send()

        if all(prices != None) and all(SMA200s != None):
            ind_B = np.sign(prices - SMA200s)
            if ind_B[0] == 0:
                logger.debug(prices, SMA200s)

            if np.sum(ind_B) == 0 and any(ind_B) != 0:
                logger.debug("Ind_B difference:" + str(ind_B))
                alert_B = TelegramAlert(
                    coin=self.coin,
                    signal="SMA",
                    trend=int(ind_B[0]),
                    horizon=horizons[self.period],
                    strength_value=int(2),
                    strength_max=int(3)

                )
                alert_B.print()
                alert_B.send()

        if all(SMA200s != None) and all(SMA50s != None):
            ind_C = np.sign(SMA50s - SMA200s)
            if ind_C[0] == 0:
                logger.debug(SMA50s, SMA200s)

            if np.sum(ind_C) == 0 and any(ind_C) != 0:
                logger.debug("Ind_C difference:" + str(ind_C))
                alert_C = TelegramAlert(
                    coin=self.coin,
                    signal="SMA",
                    trend=int(ind_C[0]),
                    horizon=horizons[self.period],
                    strength_value=int(3),
                    strength_max=int(3)

                )
                alert_C.print()
                alert_C.send()

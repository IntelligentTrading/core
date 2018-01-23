from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models import price_resampl
from settings import time_speed
import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)
SMA_LIST = [9, 20, 26, 30, 50, 52, 60, 120, 200]

class Sma(AbstractIndicator):

    sma_period = models.PositiveSmallIntegerField(null=False, default=50)
    sma_high_price = models.BigIntegerField(null=True)
    sma_close_price = models.BigIntegerField(null=True)
    sma_midpoint_price = models.BigIntegerField(null=True)

    def _compute_sma(self):
        # get neccesary records from price_resample
        #logger.debug(" compute SMA starts")
        resampl_prices_df = price_resampl.get_n_last_resampl_df(
            self.resample_period * self.sma_period + 5,
            self.source,
            self.transaction_currency,
            self.counter_currency,
            self.resample_period
        )
        resampl_close_price_ts = resampl_prices_df.close_price
        resampl_high_price_ts = resampl_prices_df.high_price
        resampl_midpoint_price_ts = resampl_prices_df.midpoint_price
        time_max = np.max(resampl_prices_df.index)

        # reduce smawindow if we are in test mode
        sma_window = int(self.sma_period/time_speed)
        #calculte sma if half of the nessesary time points are present
        min_per = int(sma_window/2) if sma_window > 10 else None

        if not resampl_close_price_ts.empty:
            sma_close_ts = resampl_close_price_ts.rolling(window=sma_window, center=False, min_periods=min_per).mean()
            if not np.isnan(sma_close_ts[time_max]):
                self.sma_close_price = int(sma_close_ts[time_max])
        else:
            logger.debug(' Not enough CLOSE prices for SMA calculation, resample_period=' + str(self.resample_period) )

        if not resampl_high_price_ts.empty:
            # calculate SMA
            sma_high_ts = resampl_high_price_ts.rolling(window=sma_window, center=False, min_periods=min_per).mean()
            if not np.isnan(sma_high_ts[time_max]):
                self.sma_high_price = int(sma_high_ts[time_max])
        else:
            logger.debug(' Not enough HIGH prices for SMA calculation, resample_period=' + str(self.resample_period) )


        if not resampl_midpoint_price_ts.empty:
            sma_midpoint_ts = resampl_midpoint_price_ts.rolling(window=sma_window, center=False, min_periods=min_per).mean()
            if not np.isnan(sma_midpoint_ts[time_max]):
                self.sma_midpoint_price = int(sma_midpoint_ts[time_max])
        else:
            logger.debug(' Not enough MIDPOINT prices for SMA calculation, resample_period=' + str(self.resample_period))


    @staticmethod
    def compute_all(cls,**kwargs):

        # todo - avoid creation empty record if no sma was computed..it also mith be fine
        for sma_period in SMA_LIST:
            try:
                sma_instance = cls.objects.create(**kwargs, sma_period = sma_period)
                sma_instance._compute_sma()
                sma_instance.save()
                #logger.debug("   ...SMA_" + str(sma_period) +" calculation done and saved.")
            except Exception as e:
                logger.error(" SMA " + str(sma_period) + "Compute Exception: " + str(e))
        logger.debug("   ...All SMA calculations have been done and saved.")





####################### get n last sma records as a DataFrame
# NOTE : dont use **kwarg because we dont use time parameter here, to avoid confusion
def get_n_last_sma_df(n, sma_period, source, transaction_currency, counter_currency, resample_period):

    last_prices = list(Sma.objects.filter(
        timestamp__gte=datetime.now() - timedelta(minutes=(resample_period * sma_period * n)),
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        resample_period=resample_period,
        sma_period=sma_period,
    ).order_by('-timestamp').values('timestamp','sma_close_price','sma_midpoint_price'))

    df = pd.DataFrame()
    if last_prices:
        ts = [rec['timestamp'] for rec in last_prices]
        sma_close_prices = pd.Series(data=[rec['sma_close_price'] for rec in last_prices], index=ts)
        sma_midpoint_prices = pd.Series(data=[rec['sma_midpoint_price'] for rec in last_prices], index=ts)

        df['sma_close_price'] = sma_close_prices
        df['sma_midpoint_price'] = sma_midpoint_prices

    return df.iloc[::-1]

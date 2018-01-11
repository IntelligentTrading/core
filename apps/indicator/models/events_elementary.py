from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models.rsi import get_last_rs_object
from apps.indicator.models.sma import get_n_last_sma_ts
from apps.indicator.models.price_resampl import get_n_last_close_price_ts

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EventsElementary(AbstractIndicator):
    event_name = models.CharField(max_length=32, null=False, blank=False, default="none")
    event_value = models.IntegerField(null=True)
    event_second_value = models.FloatField(null=True)

    '''
    def _calculate_kumo_breakout    
    
    @staticmethod
    def run_all_events_calculation
    def get_event_table(coin, from,to)
    
    '''



    @staticmethod
    def run_events_check(cls, timestamp, source, transaction_currency, counter_currency, resample_period):

        # check for rsi events
        rs_obj = get_last_rs_object(timestamp, source, transaction_currency, counter_currency, resample_period)
        rsi_bracket = rs_obj.get_rsi_bracket_value()
        if rsi_bracket != 0:
            new_instance = cls.objects.create(
                timestamp=timestamp,
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency,
                resample_period=resample_period,
                event_name = "rsi_bracket",
                event_value = rsi_bracket,
                event_second_value = rs_obj.rsi,
            )
            logger.debug("   ...Events_RSI calculations done and saved.")
        logger.debug("   ... No RSI signals.")


        # check SMA cross over events
        # NOTE - correct df names if change sma_low!
        SMA_LOW = 50
        SMA_HIGN = 120 #200
        price_ts = get_n_last_close_price_ts(10, source, transaction_currency, counter_currency, resample_period)
        sma_low_ts = get_n_last_sma_ts(10, SMA_LOW, source, transaction_currency, counter_currency, resample_period)
        sma_high_ts = get_n_last_sma_ts(10, SMA_HIGN, source, transaction_currency, counter_currency, resample_period)

        df = pd.DataFrame({
            #'idx_col': price_ts.index,
            'closing': price_ts,
            'low': sma_low_ts,
            'high': sma_high_ts
        })


        df['sma50_cross_price_down'] = np.sign(df.low - df.closing).diff().lt(0)  # -1
        df['sma200_cross_price_down'] = np.sign(df.high - df.closing).diff().lt(0) # -2
        df['sma50_cross_sma200_down'] = np.sign(df.low - df.high).diff().lt(0) # -3

        df['sma50_cross_price_up'] = np.sign(df.low - df.closing).diff().gt(0) # 1
        df['sma200_cross_price_up'] = np.sign(df.high - df.closing).diff().gt(0) # 2
        df['sma50_cross_sma200_up'] = np.sign(df.low - df.high).diff().gt(0)  # 3

        # get the last records of most reacent events
        last_events_df = df[[
            'sma50_cross_price_down',
            'sma200_cross_price_down',
            'sma50_cross_sma200_down',
            'sma50_cross_price_up',
            'sma200_cross_price_up',
            'sma50_cross_sma200_up'
            ]].tail(1)

        # save event if any of then have happend
        for column in last_events_df:
            if last_events_df[column].bool():
                new_instance = cls.objects.create(
                    timestamp=timestamp,
                    source=source,
                    transaction_currency=transaction_currency,
                    counter_currency=counter_currency,
                    resample_period=resample_period,
                    event_name=column,
                    event_value=int(1),
                )
                logger.debug("   ...FIRED - Event " + column)
            logger.debug("   ...No Events for " + column)

        # todo - check and save ichimoku elementary events


        # continue to complex boolean events?





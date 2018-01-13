from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.signal.models.signal import Signal
from apps.indicator.models.rsi import get_last_rs_object
from apps.indicator.models.sma import get_n_last_sma_df
from apps.indicator.models.price_resampl import get_n_last_resampl_df
from apps.user.models.user import get_horizon_value_from_string
from settings import HORIZONS_TIME2NAMES

from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EventsElementary(AbstractIndicator):
    event_name = models.CharField(max_length=32, null=False, blank=False, default="none")
    event_value = models.IntegerField(null=True)
    event_second_value = models.FloatField(null=True)



    @staticmethod
    def check_events(cls, **kwargs):
        source = kwargs['source']
        transaction_currency = kwargs['transaction_currency']
        counter_currency = kwargs['counter_currency']
        resample_period = kwargs['resample_period']

        _col2trend = {
            'sma50_cross_price_down': -1,
            'sma200_cross_price_down': -2,
            'sma50_cross_sma200_down': -3,
            'sma50_cross_price_up': 1,
            'sma200_cross_price_up': 2,
            'sma50_cross_sma200_up': 3
        }
        horizon = get_horizon_value_from_string(display_string=HORIZONS_TIME2NAMES[resample_period])

        ##### check for rsi events, save and emit signal
        rs_obj = get_last_rs_object(**kwargs)
        if rs_obj is not None:
            rsi_bracket = rs_obj.get_rsi_bracket_value()
            if rsi_bracket != 0:
                # save the event
                new_instance = cls.objects.create(
                    **kwargs,
                    event_name = "rsi_bracket",
                    event_value = rsi_bracket,
                    event_second_value = rs_obj.rsi,
                )
                # emit signal
                signal_rsi = Signal(
                    **kwargs,
                    signal='RSI',
                    rsi_value=rs_obj.rsi,
                    trend=np.sign(rsi_bracket),
                    horizon=horizon,
                    strength_value=np.abs(rsi_bracket),
                    strength_max=int(3),
                )
                signal_rsi.save()
                logger.debug("   ...Events_RSI calculations done and saved.")
        logger.debug("   ... No RSI signals.")


        ###### check SMA cross over events
        # NOTE - correct df names if change sma_low!
        SMA_LOW = 50
        SMA_HIGN = 200
        prices_df = get_n_last_resampl_df(10, source, transaction_currency, counter_currency, resample_period)
        sma_low_df = get_n_last_sma_df(10, SMA_LOW, source, transaction_currency, counter_currency, resample_period)
        sma_high_df = get_n_last_sma_df(10, SMA_HIGN, source, transaction_currency, counter_currency, resample_period)

        prices_df['low_sma'] = sma_low_df.sma_close_price
        prices_df['high_sma'] = sma_high_df.sma_close_price

        # calculate all events and place them to one DF
        events_df = pd.DataFrame()
        events_df['sma50_cross_price_down'] = np.sign(prices_df.low_sma - prices_df.close_price).diff().lt(0)  # -1
        events_df['sma200_cross_price_down'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().lt(0) # -2
        events_df['sma50_cross_sma200_down'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().lt(0) # -3
        events_df['sma50_cross_price_up'] = np.sign(prices_df.low_sma - prices_df.close_price).diff().gt(0) # 1
        events_df['sma200_cross_price_up'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().gt(0) # 2
        events_df['sma50_cross_sma200_up'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().gt(0)  # 3

        time_max = events_df.idxmax()[0]
        series = events_df.loc[time_max]

        # for each event in last row of all recents events
        for event_name, event_value in series.iteritems():
            # if events is TRUE
            if event_value:
                trend = _col2trend[event_name]
                new_instance = cls.objects.create(
                    **kwargs,
                    event_name=event_name,
                    event_value=int(1),
                )
                signal_sma_cross = Signal(
                    **kwargs,
                    signal='SMA',
                    trend=np.sign(trend), # -1 / 1
                    horizon=horizon,
                    strength_value=np.abs(trend), # 1,2,3
                    strength_max=int(3)
                )
                signal_sma_cross.save()
                logger.debug("   ...FIRED - Event " + event_name)
            logger.debug("   ...No Events for " + event_name)

        ####### ichimoku elementary events




###################
def get_most_recent_events_df(**kwargs):

    last_events_obj = EventsElementary.objects.filter(**kwargs)

    if not last_events_obj:
        return None

    # convert several records to a df with columns
    df = pd.DataFrame()
    for event in last_events_obj:
        df[event.event_name] = pd.Series(event.event_value)
    # {'idx_col': pd.DatetimeIndex(timestamp)}

    return df




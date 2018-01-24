from django.db import models
from settings import HORIZONS_TIME2NAMES, LONG

from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.signal.models.signal import Signal
from apps.indicator.models.events_elementary import get_last_elementory_events_df
from apps.indicator.models.rsi import get_last_rs_object
from apps.user.models.user import get_horizon_value_from_string

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EventsLogical(AbstractIndicator):
    event_name = models.CharField(max_length=32, null=False, blank=False, default="none")
    event_value = models.IntegerField(null=True)

    @staticmethod
    def check_events(cls, **kwargs):
        resample_period = kwargs['resample_period']
        horizon = get_horizon_value_from_string(display_string=HORIZONS_TIME2NAMES[resample_period])

        # get all elementory events
        all_events_df = get_last_elementory_events_df(**kwargs)
        curr_event_df = all_events_df.iloc[-1]

        # get events for long time period (not for current)
        long_param_dict = kwargs
        long_param_dict['resample_period'] = LONG
        all_long_period_events_df = get_last_elementory_events_df(**long_param_dict)
        long_period_events_df = all_long_period_events_df.iloc[-1]

        # add a long period signal to the current signals
        if not long_period_events_df.empty:
            curr_event_df['long_sma50_cross_sma200_up'] = long_period_events_df['sma50_cross_sma200_up']
        else:
            curr_event_df['long_sma50_cross_sma200_up'] = 0


        if not curr_event_df.empty:
            # print all events if any
            for column in curr_event_df:
                logger.debug('    ... event: ' + column + ' = ' + str(curr_event_df[column].values))

            ###################### Ichi kumo breakout UP
            logger.debug("   ... Check Ichimoku Breakout UP Event ")
            curr_event_df['kumo_breakout_up_rules'] = np.where(
                (curr_event_df.closing_cloud_breakout_up_extended &
                 curr_event_df.lagging_above_cloud &
                 curr_event_df.lagging_above_highest &
                 curr_event_df.conversion_above_base
                 ) == True,
                1, 0)

            # detect the fact of the break out, so emit signal only once
            curr_event_df['kumo_breakout_up_signals'] = curr_event_df.kumo_breakout_up_rules.diff().gt(0)

            # save logical event and emit signal
            if curr_event_df['kumo_breakout_up_signals'].values:
                logger.debug('    YOH! Kumo breakout UP has been FIRED!')
                kumo_event = cls.objects.create(
                    **kwargs,
                    event_name='kumo_breakout_up_signals',
                    event_value=int(1),
                )
                signal_kumo = Signal(
                    **kwargs,
                    signal='kumo_breakout',
                    trend = int(1),  # positive trend means it is UP / bullish signal
                    horizon=horizon,
                )

            ######################## Ichi kumo breakout DOWN
            logger.debug("   ... Check Ichimoku Breakout DOWN Event ")
            curr_event_df['kumo_breakout_down_rules'] = np.where(
                (curr_event_df.closing_cloud_breakout_down_extended &
                 curr_event_df.lagging_below_cloud &
                 curr_event_df.lagging_below_lowest &
                 curr_event_df.conversion_below_base
                 ) == True,
                1, 0)

            # detect the fact of the break out, so emit signal only once
            curr_event_df['kumo_breakout_down_signals'] = curr_event_df.kumo_breakout_down_rules.diff().gt(0)

            # save logical event and emit signal
            if curr_event_df['kumo_breakout_down_signals'].values:
                logger.debug('    YOH! Kumo breakout DOWN has been FIRED!')
                kumo_event = cls.objects.create(
                    **kwargs,
                    event_name='kumo_breakout_down_signals',
                    event_value=int(1),
                )
                signal_kumo = Signal(
                    **kwargs,
                    signal='kumo_breakout',
                    trend=int(-1),  # negative is bearish
                    horizon=horizon,
                )


            ##### check for ITT Cummulative RSI Signal
            logger.debug("   ... Check RSI Cumulative Event ")

            curr_event_df['RSI_Cumulative'] = np.where(
                (
                    curr_event_df['long_sma50_cross_sma200_up'] &
                    np.abs(curr_event_df['rsi_bracket']) == 3
                 ) == True,
                1, 0)

            if curr_event_df['RSI_Cumulative'].values:
                logger.debug('    YOH! RSI_Cummulative has been FIRED!')
                rsi_cum = cls.objects.create(
                    **kwargs,
                    event_name='RSI_Cumulative',
                    event_value=np.sign(curr_event_df['rsi_bracket']),
                )
                rs_obj = get_last_rs_object(**kwargs)
                signal_rsi_cum = Signal(
                    **kwargs,
                    signal='RSI_Cumulative',
                    rsi_value=rs_obj.rsi,
                    trend=np.sign(curr_event_df['rsi_bracket']),
                    horizon=horizon,
                )

        else:
            logger.debug("   ... No elementary events found at all, skip processing !")
            return pd.DataFrame()


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

        if not all_events_df.empty:
            curr_events_df = all_events_df.iloc[-1]   # get the last row
            # print all events if any
            for name, values in curr_events_df.iteritems():
                logger.debug('    ... event: ' + name + ' = ' + str(curr_events_df[values]))

            ###################### Ichi kumo breakout UP
            logger.debug("   ... Check Ichimoku Breakout UP Event ")
            all_events_df['kumo_breakout_up_rules'] = np.where(
                (all_events_df.closing_cloud_breakout_up_extended &
                 all_events_df.lagging_above_cloud &
                 all_events_df.lagging_above_highest &
                 all_events_df.conversion_above_base
                 ) == True,
                1, 0)

            # detect the fact of the break out and add the column event to DF
            all_events_df['kumo_breakout_up_signals'] = all_events_df.kumo_breakout_up_rules.diff().gt(0)
            curr_events_df = all_events_df.iloc[-1]  # again

            # save logical event and emit signal
            if curr_events_df['kumo_breakout_up_signals']:
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
            else:
                logger.debug("   ... No kumo_breakout_up_signals")

            ######################## Ichi kumo breakout DOWN
            logger.debug("   ... Check Ichimoku Breakout DOWN Event ")
            all_events_df['kumo_breakout_down_rules'] = np.where(
                (all_events_df.closing_cloud_breakout_down_extended &
                 all_events_df.lagging_below_cloud &
                 all_events_df.lagging_below_lowest &
                 all_events_df.conversion_below_base
                 ) == True,
                1, 0)

            # detect the fact of the break out, so emit signal only once
            all_events_df['kumo_breakout_down_signals'] = all_events_df.kumo_breakout_down_rules.diff().gt(0)
            curr_events_df = all_events_df.iloc[-1]  # again

            # save logical event and emit signal
            if curr_events_df['kumo_breakout_down_signals']:
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
            else:
                logger.debug("   ... No kumo_breakout_down events.")


            ########## check for ITT Cummulative RSI Signal
            logger.debug("   ... Check RSI Cumulative Event ")

            # get events for long time period (not for current)
            long_param_dict = kwargs
            long_param_dict['resample_period'] = LONG
            all_long_period_events_df = get_last_elementory_events_df(**long_param_dict)

            # add a long period signal to the current signals
            if not all_long_period_events_df.empty:
                long_period_events_df = all_long_period_events_df.iloc[-1]  # get the last record
                all_long_period_events_df['long_sma50_cross_sma200_up'] = long_period_events_df['sma50_cross_sma200_up']

                all_long_period_events_df['RSI_Cumulative'] = np.where(
                (
                    all_long_period_events_df['long_sma50_cross_sma200_up'] &
                    np.abs(all_long_period_events_df['rsi_bracket']) == 3
                 ) == True,
                1, 0)

                curr_events_df = all_events_df.iloc[-1]  # again

                if curr_events_df['RSI_Cumulative']:
                    logger.debug('    YOH! RSI_Cummulative has been FIRED!')
                    rsi_cum = cls.objects.create(
                        **kwargs,
                        event_name='RSI_Cumulative',
                        event_value=np.sign(curr_events_df['rsi_bracket']),
                    )
                    rs_obj = get_last_rs_object(**kwargs)
                    signal_rsi_cum = Signal(
                        **kwargs,
                        signal='RSI_Cumulative',
                        rsi_value=rs_obj.rsi,
                        trend=np.sign(curr_events_df['rsi_bracket']),
                        horizon=horizon,
                    )
            else:
                logger.debug("   ... No RSI Cumulative events.")

        else:
            logger.debug("   ... No elementary events found at all, skip processing !")
            return pd.DataFrame()


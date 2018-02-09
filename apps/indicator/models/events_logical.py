from django.db import models
from settings import HORIZONS_TIME2NAMES, LONG

from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.signal.models.signal import Signal
from apps.indicator.models.events_elementary import get_current_elementory_events_df, get_last_ever_entered_elementory_events_df
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

        logger.info('   ::::  Start analysing LOGICAL events ::::')
        # get all elementory events
        # always one line!
        last_events_df = get_current_elementory_events_df(**kwargs)

        if not last_events_df.empty:
            ###################### Ichi kumo breakout UP
            logger.debug("   ... Check Ichimoku Breakout UP Event ")

            last_events_df['kumo_breakout_up_signal'] = np.where(
                (last_events_df.close_cloud_breakout_up_ext &
                 last_events_df.lagging_above_cloud &
                 last_events_df.lagging_above_highest &
                 last_events_df.conversion_above_base
                 ) == True,
                1, 0)

            # save logical event and emit signal - we need all because it is s Series
            if all(last_events_df['kumo_breakout_up_signal']):

                try:
                    kumo_event = cls.objects.create(
                        **kwargs,
                        event_name='kumo_breakout_up_signal',
                        event_value=int(1),
                    )
                    signal_kumo_up = Signal(
                        **kwargs,
                        signal='kumo_breakout',
                        trend = int(1),  # positive trend means it is UP / bullish signal
                        horizon=horizon,
                    )
                    signal_kumo_up.save()
                    logger.info('  >>> YOH! Kumo breakout UP has been FIRED!')
                except Exception as e:
                    logger.error(" Error saving kumo_breakout_up_signal ")
            else:
                logger.debug("   .. No kumo_breakout_up_signals")


            ######################## Ichi kumo breakout DOWN
            logger.debug("   ... Check Ichimoku Breakout DOWN Event ")

            last_events_df['kumo_breakout_down_signal'] = np.where(
                (last_events_df.close_cloud_breakout_down_ext &
                 last_events_df.lagging_below_cloud &
                 last_events_df.lagging_below_cloud &
                 last_events_df.conversion_below_base
                 ) == True,
                1, 0)

            # save logical event and emit signal
            if all(last_events_df['kumo_breakout_down_signal']):

                try:
                    kumo_event = cls.objects.create(
                        **kwargs,
                        event_name='kumo_breakout_down_signal',
                        event_value=int(1),
                    )
                    signal_kumo_down = Signal(
                        **kwargs,
                        signal='kumo_breakout',
                        trend=int(-1),  # negative is bearish
                        horizon=horizon,
                    )
                    signal_kumo_down.save()
                    logger.info('   >>> YOH! Kumo breakout DOWN has been FIRED!')
                except Exception as e:
                    logger.error(" Error saving kumo_breakout_down_signal ")

            else:
                logger.debug("   .. No kumo_breakout_down events.")

            # DEBUG: print all events if any
            for name, values in last_events_df.iteritems():
                if values[0]:
                    logger.debug('    ... event: ' + name + ' = ' + str(values[0]) )


            ########## check for ITT Cummulative RSI Signal
            logger.debug("   ... Check RSI Cumulative Event ")

            # get events for long time period (not for current)
            long_param_dict = kwargs
            long_param_dict['resample_period'] = LONG
            long_period_events_df = get_last_ever_entered_elementory_events_df(**long_param_dict)

            # add a long period signal to the current signals
            if not long_period_events_df.empty:
                last_events_df['long_sma50_above_sma200'] = long_period_events_df['sma50_above_sma200']

                last_events_df['RSI_Cumulative'] = np.where(
                (
                    last_events_df['long_sma50_above_sma200'] &
                    np.abs(last_events_df['rsi_bracket']) == 3
                 ) == True,
                1, 0)


                if all(last_events_df['RSI_Cumulative']):

                    try:
                        rsi_cum = cls.objects.create(
                            **kwargs,
                            event_name='RSI_Cumulative',
                            event_value=np.sign(last_events_df['rsi_bracket']),
                        )
                        rs_obj = get_last_rs_object(**kwargs)
                        signal_rsi_cum = Signal(
                            **kwargs,
                            signal='RSI_Cumulative',
                            rsi_value=rs_obj.rsi,
                            trend=np.sign(last_events_df['rsi_bracket']),
                            horizon=horizon,
                        )
                        signal_rsi_cum.save()
                        logger.info('    YOH! RSI_Cummulative has been FIRED!')
                    except Exception as e:
                        logger.error(" Error saving RSI Cumulative signal ")

            else:
                logger.debug("   .. No RSI Cumulative events.")

        else:
            logger.debug("   ... No elementary events found at all, skip processing !")
            return pd.DataFrame()


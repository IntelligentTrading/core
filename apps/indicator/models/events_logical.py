from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.signal.models.signal import Signal
from apps.indicator.models.events_elementary import get_last_elementory_events_df
from apps.indicator.models.price_resampl import get_n_last_resampl_df
from apps.user.models.user import get_horizon_value_from_string
from settings import HORIZONS_TIME2NAMES


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

        e_df = get_last_elementory_events_df(**kwargs)

        #######  calculate logical  Ichimoku signals
        if not e_df.empty:
            for column in e_df:
                logger.debug('    ... event: ' + column + ' = ' + str(e_df[column].values))

            e_df['kumo_breakout_up_rules'] = np.where(
                (e_df.closing_cloud_breakout_up_extended &
                 e_df.lagging_above_cloud &
                 e_df.lagging_above_highest &
                 e_df.conversion_above_base
                 ) == True,
                1, 0)

            e_df['kumo_breakout_up_signals'] = e_df.kumo_breakout_up_rules.diff().gt(0)
            if e_df['kumo_breakout_up_signals'].values:
                logger.debug('    YOH! Kumo breakout FIRED!')
                kumo_event = cls.objects.create(
                    **kwargs,
                    event_name='kumo_breakout_up_signals',
                    event_value=int(1),
                )
                signal_kumo = Signal(
                    **kwargs,
                    signal='kumo_breakout_up_signals',
                    horizon=horizon,
                )
        else:
            return pd.DataFrame()
            #logger.debug("   ... No Ichimoku elementary event at all!")

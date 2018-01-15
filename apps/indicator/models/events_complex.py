from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models.events_elementary import get_most_recent_events_df
from apps.indicator.models.price_resampl import get_n_last_resampl_df

import pandas as pd
import numpy as np

class EventsComplex(AbstractIndicator):
    pass

    @staticmethod
    def check_events(cls, timestamp, source, transaction_currency, counter_currency, resample_period):
        e_df = get_most_recent_events_df(timestamp, source, transaction_currency, counter_currency, resample_period)

        #######  calculate logical  Ichimoku signals

        e_df['kumo_breakout_up_rules'] = np.where(
            (e_df.closing_cloud_breakout_up_extended &
             e_df.lagging_above_cloud &
             e_df.lagging_above_highest &
             e_df.conversion_above_base
             ) == True,
            1, 0)

        e_df['kumo_breakout_up_signals'] = e_df.kumo_breakout_up_rules.diff().gt(0)

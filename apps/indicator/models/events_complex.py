from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models.events_elementary import get_most_recent_events_df
from apps.indicator.models.price_resampl import get_n_last_resampl_df

class EventsComplex(AbstractIndicator):
    pass

    @staticmethod
    def check_events(cls, timestamp, source, transaction_currency, counter_currency, resample_period):
        prices_df = get_n_last_resampl_df(10, source, transaction_currency, counter_currency, resample_period)
        events_df = get_most_recent_events_df(timestamp, source, transaction_currency, counter_currency, resample_period)

        #######  check Ichimoku signals
        '''
        tenkan_sen_conversion = midpoint_price_ts.rolling(window=par_1_9, center=False, min_periods=5).mean()
        kijun_sen_base = midpoint_price_ts.rolling(window=par_2_26, center=False, min_periods=15).mean()
        senkou_span_a_leading = ((tenkan_sen_conversion + kijun_sen_base) / 2).shift(par_2_26)
        period52 = midpoint_price_ts.rolling(window=par_3_52, center=False, min_periods=25).mean()
        senkou_span_b_leading = period52.shift(par_2_26)
        hikou_span_lagging = closing_price_ts.shift(-par_2_26)

        # combine everythin into one dataFrame
        df = pd.DataFrame({
            'idx_col': price_low_ts.index,
            'low': price_low_ts,
            'high': price_high_ts,
            'closing': closing_price_ts,
            'open': open_price_ts,
            'conversion': tenkan_sen_conversion,
            'base': kijun_sen_base,
            'leading_a': senkou_span_a_leading,
            'leading_b': senkou_span_b_leading,
            'lagging': hikou_span_lagging
        })
        '''
        pass

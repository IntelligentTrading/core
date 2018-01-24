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

ALL_POSSIBLE_ELEMENTARY_EVENTS = [
    'sma50_cross_price_down',
    'sma200_cross_price_down',
    'sma50_cross_sma200_down',
    'sma50_cross_price_up',
    'sma200_cross_price_up',
    'sma50_cross_sma200_up',
    'rsi_bracket',
    'closing_cloud_breakout_up_extended',
    'closing_cloud_breakout_down_extended',
    'lagging_above_cloud',
    'lagging_below_cloud',
    'lagging_above_highest',
    'lagging_below_lowest',
    'conversion_above_base',
    'conversion_below_base'
]

_col2trend = {
    'sma50_cross_price_down': -1,
    'sma200_cross_price_down': -2,
    'sma50_cross_sma200_down': -3,
    'sma50_cross_price_up': 1,
    'sma200_cross_price_up': 2,
    'sma50_cross_sma200_up': 3
}


# plot Ichi for debug
def _draw_cloud(df,**kwargs):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter, OldScalarFormatter
    from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
    import matplotlib.ticker as plticker

    transaction_currency = kwargs['transaction_currency']
    counter_currency = kwargs['counter_currency']
    resample_period = kwargs['resample_period']

    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(16, 5))
    fig.suptitle("%s/%d Ichimoku Cloud" % (transaction_currency, counter_currency))
    #ax1.xaxis.set_major_formatter(DateFormatter("%d-%m"))

    fmt = ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax1.yaxis.set_major_formatter(fmt)

    ax1.grid(True)
    loc = plticker.MultipleLocator(base=1.0)  # this locator puts ticks at regular intervals
    ax1.xaxis.set_major_locator(loc)

    # candlestick_ohlc(ax1, df_candle)

    ax1.plot(df.high, color='black', linewidth=2)
    #ax1.plot(df.low, color='black', linewidth=2)
    ax1.plot(df.conversion, linestyle=':', color='orange')
    ax1.plot(df.base, linestyle=':', color='orange')
    ax1.plot(df.leading_a, linestyle='--', color='magenta')
    ax1.plot(df.leading_b, linestyle='-', color='magenta')
    ax1.fill_between(df.senkou_span_a_leading.index, df.leading_a, df.leading_b, color='lightskyblue')

    ax1.plot(df.hikou_span_lagging, linestyle='-', color='lightblue')

def _process_rsi(horizon, **kwargs):
    rs_obj = get_last_rs_object(**kwargs)

    if (rs_obj is not None) & (rs_obj.rsi is not None):
        rsi_bracket = rs_obj.get_rsi_bracket_value()
        if rsi_bracket != 0:
            # save the event
            new_instance = EventsElementary.objects.create(
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
    #logger.debug("   ... No RSI events.")


def _process_sma_crossovers(time_current, horizon, prices_df, **kwargs):

    # NOTE - correct df names if change sma_low!
    # sma50_cross_price_down

    # calculate all events and place them to one DF
    events_df = pd.DataFrame()
    events_df['sma50_cross_price_down'] = np.sign(prices_df.low_sma - prices_df.close_price).diff().lt(0)  # -1
    events_df['sma200_cross_price_down'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().lt(0)  # -2
    events_df['sma50_cross_sma200_down'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().lt(0)  # -3
    events_df['sma50_cross_price_up'] = np.sign(prices_df.low_sma - prices_df.close_price).diff().gt(0)  # 1
    events_df['sma200_cross_price_up'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().gt(0)  # 2
    events_df['sma50_cross_sma200_up'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().gt(0)  # 3

    # time_max2 = events_df.idxmax()[0]
    # get the last events row and account for a small timestamp rounding error
    last_event_row = events_df.iloc[-1]
    time_of_last_row = events_df.index[-1]
    assert(abs(time_current-time_of_last_row).value < 1800000)  # check if difference with now now > 30min

    # for each event in last row of all recents events
    for event_name, event_value in last_event_row.iteritems():
        if event_value:    # if one of SMA events is TRUE, save and emit
            trend = _col2trend[event_name]
            sma_event = EventsElementary.objects.create(
                **kwargs,
                event_name=event_name,
                event_value=int(1),
            )
            sma_event.save()

            signal_sma_cross = Signal(
                **kwargs,
                signal='SMA',
                trend=np.sign(trend),  # -1 / 1
                horizon=horizon,
                strength_value=np.abs(trend),  # 1,2,3
                strength_max=int(3)
            )
            signal_sma_cross.save()
            logger.debug("   ...FIRED - Event " + event_name)
            # logger.debug("   ...No Events for " + event_name)




class EventsElementary(AbstractIndicator):
    event_name = models.CharField(max_length=32, null=False, blank=False, default="none")
    event_value = models.IntegerField(null=True)
    event_second_value = models.FloatField(null=True)

    @staticmethod
    def check_events(cls, **kwargs):
        timestamp = kwargs['timestamp']
        source = kwargs['source']
        transaction_currency = kwargs['transaction_currency']
        counter_currency = kwargs['counter_currency']
        resample_period = kwargs['resample_period']


        horizon = get_horizon_value_from_string(display_string=HORIZONS_TIME2NAMES[resample_period])
        time_current = pd.to_datetime(timestamp, unit='s')

        # set Ichimoku parameters
        ichi_param_1_9 = 20
        ichi_param_2_26 = 60
        ichi_param_3_52 = 120
        ichi_param_4_26 = 30

        # load nessesary resampled prices from price resampled
        # we only need last_records back in time
        last_records = ichi_param_4_26 + ichi_param_4_26 + 10
        prices_df = get_n_last_resampl_df(last_records, source, transaction_currency, counter_currency, resample_period)

        ###### check for rsi events, save and emit signal
        logger.debug("   ... Check RSI Events: ")
        _process_rsi(horizon, **kwargs)


        ############## check SMA cross over events
        SMA_LOW = 50
        SMA_HIGH = 200
        sma_low_df = get_n_last_sma_df(last_records, SMA_LOW, source, transaction_currency, counter_currency,
                                       resample_period)
        sma_high_df = get_n_last_sma_df(last_records, SMA_HIGH, source, transaction_currency, counter_currency,
                                        resample_period)

        # add SMA to price column to dataframe
        prices_df['low_sma'] = sma_low_df.sma_close_price
        prices_df['high_sma'] = sma_high_df.sma_close_price
        # todo: that is not right fron statistical view point!!! remove later when anough values
        prices_df = prices_df.fillna(value=0)

        logger.debug("   ... Check SMA Events: ")
        # todo - add return value, and say if any crossovers have happend
        _process_sma_crossovers(time_current, horizon, prices_df, **kwargs)


        ############## calculate and save ICHIMOKU elementary events
        # no signal emitting

        logger.debug("   ... Check Ichimoku Elementary Events: ")
        price_low_ts = prices_df['low_price']
        price_high_ts = prices_df['high_price']
        closing_price_ts = prices_df['close_price']
        midpoint_price_ts = prices_df['midpoint_price']

        # calculate new line indicators as time series
        tenkan_sen_conversion = midpoint_price_ts.rolling(window=ichi_param_1_9, center=False, min_periods=4).mean()
        kijun_sen_base = midpoint_price_ts.rolling(window=ichi_param_2_26, center=False, min_periods=12).mean()

        senkou_span_a_leading = ((tenkan_sen_conversion + kijun_sen_base) / 2).shift(ichi_param_2_26)
        period52 = midpoint_price_ts.rolling(window=ichi_param_3_52, center=False, min_periods=25).mean()

        senkou_span_b_leading = period52.shift(ichi_param_2_26)
        hikou_span_lagging = closing_price_ts.shift(-ichi_param_2_26)

        # combine everythin into one dataFrame
        df = pd.DataFrame({
            'idx_col': closing_price_ts.index,
            'low': price_low_ts,
            'high': price_high_ts,
            'closing': closing_price_ts,
            'conversion': tenkan_sen_conversion,
            'base': kijun_sen_base,
            'leading_a': senkou_span_a_leading,
            'leading_b': senkou_span_b_leading,
            'lagging': hikou_span_lagging,
            'senkou_span_a_leading' : senkou_span_a_leading,
            'hikou_span_lagging' :hikou_span_lagging
        })

        # emit warning if any NAN is present
        if any(df.isnull()):
            logger.warning("  Ichi: some of the elem_events are NaN, result might be INCORRECT! ")

        df['closing_above_cloud'] = np.where(((df.closing > df.leading_a) & (df.closing > df.leading_b)), 1, 0)
        df['closing_below_cloud'] = np.where(((df.closing < df.leading_a) & (df.closing < df.leading_b)), 1, 0)

        df['closing_cloud_breakout_up'] = np.sign(
            df.closing - pd.concat([df.leading_a, df.leading_b], axis=1).max(axis=1)
        ).diff().fillna(0).gt(0)

        df['closing_cloud_breakout_down'] = np.sign(
            df.closing - pd.concat([df.leading_a, df.leading_b], axis=1).min(axis=1)
        ).diff().fillna(0).lt(0)


        # to avoid up and down noise
        df['closing_cloud_breakout_up_extended'] = df['closing_cloud_breakout_up'] | \
                                                   df['closing_cloud_breakout_up'].shift(1)

        df['closing_cloud_breakout_down_extended'] = df['closing_cloud_breakout_down'] |\
                                                     df['closing_cloud_breakout_down'].shift(1)


        # check it ichi_param_4_26 hours ago
        df['lagging_above_cloud'] = np.where(
            ((df.lagging.shift(ichi_param_4_26) > df.leading_a.shift(ichi_param_4_26)) &
             (df.lagging.shift(ichi_param_4_26) > df.leading_b.shift(ichi_param_4_26))),
            1, 0)
        # shift back to current day
        df['lagging_above_cloud'] = df['lagging_above_cloud'].shift(ichi_param_4_26)

        df['lagging_below_cloud'] = np.where(
            ((df.lagging.shift(ichi_param_4_26) < df.leading_a.shift(ichi_param_4_26)) &
             (df.lagging.shift(ichi_param_4_26) < df.leading_b.shift(ichi_param_4_26))),
            1, 0)
        df['lagging_below_cloud'] = df['lagging_below_cloud'].shift(ichi_param_4_26)


        df['lagging_above_highest'] = np.where(df.lagging.shift(ichi_param_4_26) > df.high.shift(ichi_param_4_26), 1, 0)
        df['lagging_above_highest'] = df['lagging_above_highest'].shift(ichi_param_4_26)

        df['lagging_below_lowest'] = np.where(df.lagging.shift(ichi_param_4_26) < df.low.shift(ichi_param_4_26), 1, 0)
        df['lagging_below_lowest'] = df['lagging_below_lowest'].shift(ichi_param_4_26)

        df['conversion_above_base'] = np.where(df.conversion > df.base, 1, 0)
        df['conversion_below_base'] = np.where(df.conversion < df.base, 1, 0)

        # plot - for debug
        #_draw_cloud(df, **kwargs)

        # get the last element and save as an event
        # todo: add consistency with all this event, save them in one place!
        events2save = ['closing_cloud_breakout_up_extended',
                       'closing_cloud_breakout_down_extended',
                       'lagging_above_cloud',
                       'lagging_below_cloud',
                       'lagging_above_highest',
                       'lagging_below_lowest',
                       'conversion_above_base',
                       'conversion_below_base'
                       ]

        #get the last event line in DF
        last_events = df.iloc[-1]
        time_of_last_row = df.index[-1]
        assert (abs(time_current - time_of_last_row).value < 1800000)  # check if difference with now now > 30min
        last_events = last_events.fillna(False)

        # save event in DB
        for event_name in events2save:
            event_value = last_events[event_name]
            if event_value:
                ichi_event = cls.objects.create(
                    **kwargs,
                    event_name=event_name,
                    event_value=int(1),
                )
                ichi_event.save()
                logger.debug('   ... Ichimoku elementary event FIRED : ' + str(event_name))
            #logger.debug('   ... NO Ichi event: ' + event_name )



###################
def get_last_elementory_events_df(timestamp, source, transaction_currency, counter_currency, resample_period):

    last_events = list(EventsElementary.objects.filter(
        timestamp = timestamp,
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        resample_period=resample_period,
    ).order_by('-timestamp').values('timestamp','event_name','event_value'))

    df = pd.DataFrame()
    if last_events:
        ts = [rec['timestamp'] for rec in last_events]
        event_names = pd.Series(data=[rec['event_name'] for rec in last_events], index=ts)
        event_values = pd.Series(data=[rec['event_value'] for rec in last_events], index=ts)

        df = pd.DataFrame(columns = ALL_POSSIBLE_ELEMENTARY_EVENTS, index=ts)
        df[event_names] = event_values
        df = df.fillna(value=0)
    else:
        pass
        #logger.debug("    No recent events found!")

    return df.iloc[::-1] # reverse sorting, so that the last is on the bottom

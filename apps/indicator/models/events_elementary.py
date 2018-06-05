import time
import logging
import pandas as pd
import numpy as np

from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models.price_resampl import get_n_last_resampl_df
from apps.indicator.models.sma import get_n_last_sma_df
from apps.indicator.models.rsi import Rsi
from apps.signal.models.signal import Signal
from apps.indicator.models.ann_future_price_classification import AnnPriceClassification, get_n_last_ann_classif_df

from apps.user.models.user import get_horizon_value_from_string
from settings import HORIZONS_TIME2NAMES, EMIT_RSI, EMIT_SMA, RUN_ANN, MODIFY_DB


logger = logging.getLogger(__name__)

SMA_ELEMENTARY_EVENTS =  [
    'sma50_cross_price_down',
    'sma200_cross_price_down',
    'sma50_cross_sma200_down',
    'sma50_cross_price_up',
    'sma200_cross_price_up',
    'sma50_cross_sma200_up',
    'sma50_above_sma200',
    'sma50_below_sma200',
    'rsi_bracket'
]

ICHI_ELEMENTARY_EVENTS = [
    'close_cloud_breakout_up',
    'close_cloud_breakout_down',
    'close_cloud_breakout_up_ext',
    'close_cloud_breakout_down_ext',
    'lagging_above_cloud',
    'lagging_below_cloud',
    'lagging_above_highest',
    'lagging_below_lowest',
    'conversion_above_base',
    'conversion_below_base',
    'close_above_cloud',
    'close_below_cloud',
]

AI_ELEMENTARY_EVENTS = [
    'ann_price_2class_simple'
]

# list of all events to return by get_last_elementory_events_df
ALL_POSSIBLE_ELEMENTARY_EVENTS = SMA_ELEMENTARY_EVENTS + ICHI_ELEMENTARY_EVENTS + AI_ELEMENTARY_EVENTS

# dictionary to convert name of sma event to one-number trend
_col2trend = {
    'sma50_cross_price_down': -1,
    'sma200_cross_price_down': -2,
    'sma50_cross_sma200_down': -3,
    'sma50_cross_price_up': 1,
    'sma200_cross_price_up': 2,
    'sma50_cross_sma200_up': 3
}

# Ichimoku parameters
ichi_param_1_9 = 20
ichi_param_2_26 = 60
ichi_param_3_52 = 120
ichi_displacement = 30

def _process_ai_simple(horizon, **kwargs):
    '''
    very simple strategy: emit signal anytime it changes state from up to down
    '''
    # get two reacent objects as a dataframe

    # NOTE: here I hardcoded two class classification ignoring SAME - should be don ona  model level!!

    ann_classif_df = get_n_last_ann_classif_df(4, **kwargs)
    # choose only two class classification (ignore SAME), then add a new column with the best class
    df = ann_classif_df[['probability_up','probability_down']]
    df['class'] = df.idxmax(axis=1)

    df.loc[df['class'] == 'probability_up', 'class_num'] = int(0)
    df.loc[df['class'] == 'probability_down', 'class_num'] = int(1)
    df['class_change'] = df['class_num'].diff()   # detect change of state

    # class change is a difference btw previos and current cell of class (which is Up or DOWN)
    # so in case we have  0 0 0 0 1 1 (change prediction from up to down)
    # it will generate    0 0 0 0 1 0
    if df.iloc[-1]['class_change'] != 0:
        # emit signal
        try:
            # TODO: change to emitting two signals UP and DOWN according to how others events are generated (for ML)
            new_instance = EventsElementary(
                **kwargs,
                event_name="ann_price_2class_simple",
                event_value= -int(df.iloc[-1]['class_change']),
            )
            if MODIFY_DB: new_instance.save()
            logger.debug("   >>> ANN event detected and saved")

            signal_ai = Signal(
                **kwargs,
                signal='ANN_Simple',
                trend= -int(df.iloc[-1]['class_change']),
                strength_value= int(3),
                horizon=horizon,
                predicted_ahead_for= ann_classif_df.tail(1)['predicted_ahead_for'][0],
                probability_same = ann_classif_df.tail(1)['probability_same'][0],
                probability_up = df.tail(1)['probability_up'][0],
                probability_down = df.tail(1)['probability_down'][0]
            )
            signal_ai.save()
            logger.debug("   >>> ANN event FIRED!")
        except Exception as e:
            logger.error(" Error saving/emitting ANN Event " + e)
    else:
        logger.debug("   ... no AI event generated (predicts no changes in price")



def _process_rsi(horizon, **kwargs)->int:
    '''
    at every time point get the last fresh RSI value, check the brackets of RSI
    and if we are less 25 or more 75 save this as an event in events and emit an RSI signal
    '''
    rs_obj = Rsi.objects.filter(**kwargs).last()

    if (rs_obj is not None):
        rsi_bracket = rs_obj.get_rsi_bracket_value() # get current rsi object
        if rsi_bracket != 0:
            # save the event
            try:
                new_instance = EventsElementary(
                    **kwargs,
                    event_name = "rsi_bracket",
                    event_value = rsi_bracket,
                    event_second_value = rs_obj.rsi,
                )
                if MODIFY_DB: new_instance.save()  # save if not in DEBUG mode
                logger.debug("   >>> RSI bracket event detected and saved")

                if EMIT_RSI:
                    signal_rsi = Signal(
                        **kwargs,
                        signal='RSI',
                        rsi_value=rs_obj.rsi,
                        trend=np.sign(rsi_bracket),
                        horizon=horizon,
                        strength_value=np.abs(rsi_bracket),
                        strength_max=int(3),
                    )
                    if MODIFY_DB: signal_rsi.save()
                    logger.debug("   >>> RSI bracket event FIRED!")
                else:
                    logger.debug("   .. RSI emitting disabled by settings")
            except Exception as e:
                logger.error(" Error saving/emitting RSI Event ")
            return rsi_bracket
    else:
        logger.debug(" ... No RSI Event found ")
        return False


def _process_sma_crossovers(horizon, prices_df, **kwargs):
    '''
    check if at given moment of time there is an SMA crossover event
    if so, emit a signal
    '''

    # NOTE - correct df names if change sma_low!
    time_current = pd.to_datetime(time.time(), unit='s')

    # calculate all events and place them to one DF
    events_df = pd.DataFrame()
    events_df['sma50_cross_price_down']  = np.sign(prices_df.low_sma - prices_df.close_price).diff().lt(0)  # -1
    events_df['sma200_cross_price_down'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().lt(0)  # -2
    events_df['sma50_cross_sma200_down'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().lt(0)  # -3
    events_df['sma50_cross_price_up']  = np.sign(prices_df.low_sma - prices_df.close_price).diff().gt(0)  # 1
    events_df['sma200_cross_price_up'] = np.sign(prices_df.high_sma - prices_df.close_price).diff().gt(0)  # 2
    events_df['sma50_cross_sma200_up'] = np.sign(prices_df.low_sma - prices_df.high_sma).diff().gt(0)  # 3

    events_df['sma50_above_sma200'] = np.sign(prices_df.low_sma - prices_df.high_sma).gt(0)
    events_df['sma50_below_sma200'] = np.sign(prices_df.low_sma - prices_df.high_sma).lt(0)

    # get the last events row and account for a small timestamp rounding error
    last_event_row = events_df.iloc[-1]
    time_of_last_row = events_df.index[-1]
    assert(abs( (time_current-time_of_last_row).seconds)  < 3000),'current time too far away'  # check if difference with now now > 30min

    # for each event in last row of all recents events
    for event_name, event_value in last_event_row.iteritems():
        if event_value:    # if one of SMA events is TRUE, save and emit

            # save all elem events
            try:
                sma_event = EventsElementary(
                    **kwargs,
                    event_name=event_name,
                    event_value=int(1),
                )
                if MODIFY_DB: sma_event.save()
            except Exception as e:
                logger.error(" #Error saving SMA signal ")

            # Fire all sinals, except two which we dont need and imitting is allowed
            if EMIT_SMA & (event_name not in ['sma50_above_sma200', 'sma50_below_sma200']):
                logger.debug('======> DISCREPANCY CHECK :: period= ' + str(kwargs['resample_period']) + '/ horozon= ' + str(horizon))
                try:
                    trend = _col2trend[event_name]
                    signal_sma_cross = Signal(
                        **kwargs,
                        signal='SMA',
                        trend=np.sign(trend),  # -1 / 1
                        horizon=horizon,
                        strength_value=np.abs(trend),  # 1,2,3
                        strength_max=int(3)
                    )
                    if MODIFY_DB: signal_sma_cross.save()
                    logger.debug("   >>> FIRED - Event " + event_name)
                except Exception as e:
                    logger.error(" #Error firing SMA signal ")




class EventsElementary(AbstractIndicator):
    event_name = models.CharField(max_length=32, null=False, blank=False, default="none")
    event_value = models.IntegerField(null=True)
    event_second_value = models.FloatField(null=True)

    @staticmethod
    def check_events(cls, **kwargs):
        horizon = get_horizon_value_from_string(display_string=HORIZONS_TIME2NAMES[kwargs['resample_period']])

        # create a param dict to pass inside get_n_last_resampl_df
        no_time_params = {
            'source' : kwargs['source'],
            'transaction_currency' : kwargs['transaction_currency'],
            'counter_currency' : kwargs['counter_currency'],
            'resample_period' : kwargs['resample_period']
        }

        # load nessesary resampled prices from price resampled
        # we only need last_records back in time
        last_records = ichi_displacement * ichi_displacement + 10
        prices_df = get_n_last_resampl_df(last_records, **no_time_params)
        prices_df = prices_df.fillna(value=0)

        logger.info('   ::::  Start analysing ELEMENTARY events ::::')

        ###### check for rsi events, save and emit signal
        logger.info("   ... Check RSI Events: ")
        _process_rsi(horizon, **kwargs)


        ############## check SMA cross over events
        logger.info("   ... Check SMA Events: ")
        SMA_LOW, SMA_HIGH = [50,200]

        sma_low_df = get_n_last_sma_df(last_records, SMA_LOW, **no_time_params).tail(10)
        sma_high_df = get_n_last_sma_df(last_records, SMA_HIGH, **no_time_params).tail(10)
        small_prices_df = prices_df.tail(10).copy()

        # form a small price dataframe and add SMA to price dataframe
        small_prices_df.loc[:,'low_sma'] = sma_low_df['sma_close_price']
        small_prices_df.loc[:,'high_sma'] = sma_high_df['sma_close_price']

        # todo: that is not right fron statistical view point!!! remove later when anough values
        small_prices_df = small_prices_df.fillna(value=0)


        # todo - add return value, and say if any crossovers have happend
        _process_sma_crossovers(horizon, small_prices_df, **kwargs)


        ############## calculate and save ICHIMOKU elementary events
        logger.info("   ... Check Ichimoku Elementary Events: ")

        # correct shift in 10 min , so resumple again
        # shall be removed as soon as we have time by exact hours
        # res_df = res_df[['high_price','low_price','open_price','close_price']].resample(rule='1H').mean().bfill()
        rule = str(int(kwargs['resample_period'] / 60)) + 'H'

        # todo - remove resampling when enough data is gathered (several weeks from now)
        price_low_ts = prices_df['low_price'].resample(rule=rule).mean().bfill()
        price_high_ts = prices_df['high_price'].resample(rule=rule).mean().bfill()
        closing_price_ts = prices_df['close_price'].resample(rule=rule).mean().bfill()


        # calculate five Ichi lines
        period_9_high = price_high_ts.rolling(window=ichi_param_1_9, center=False, min_periods=6).max() #highest high
        period_9_low = price_low_ts.rolling(window=ichi_param_1_9, center=False, min_periods=6).min() # lowest low
        tenkan_sen_conversion = (period_9_high + period_9_low) / 2

        period_26_high = price_high_ts.rolling(window=ichi_param_2_26, center=False, min_periods=15).max()
        period_26_low = price_low_ts.rolling(window=ichi_param_2_26, center=False, min_periods=15).min()
        kijun_sen_base = (period_26_high + period_26_low) / 2

        senkou_span_a_leading = ((tenkan_sen_conversion + kijun_sen_base) / 2).shift(ichi_displacement)

        period_52_high = price_high_ts.rolling(window=ichi_param_3_52, center=False, min_periods=25).max()
        period_52_low = price_low_ts.rolling(window=ichi_param_3_52, center=False, min_periods=25).min()
        period52 = (period_52_high + period_52_low) / 2

        senkou_span_b_leading = period52.shift(ichi_displacement)

        hikou_span_lagging = closing_price_ts.shift(-ichi_displacement)

        # combine everything into one dataFrame for convinience
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
            logger.debug("  Ichi: some of the elem_events are NaN, result might be INCORRECT! ")

        # calculate intercections and more complex events
        df['close_above_cloud'] = np.where(((df.closing > df.leading_a) & (df.closing > df.leading_b)), 1, 0)
        df['close_below_cloud'] = np.where(((df.closing < df.leading_a) & (df.closing < df.leading_b)), 1, 0)

        df['close_cloud_breakout_up'] = np.sign(
            df.closing - pd.concat([df.leading_a, df.leading_b], axis=1).max(axis=1)
        ).diff().fillna(0).gt(0)

        df['close_cloud_breakout_down'] = np.sign(
            df.closing - pd.concat([df.leading_a, df.leading_b], axis=1).min(axis=1)
        ).diff().fillna(0).lt(0)

        # to avoid up and down noise, make signal active for one more time point
        df['close_cloud_breakout_up_ext'] = df['close_cloud_breakout_up'] | df['close_cloud_breakout_up'].shift(1)
        df['close_cloud_breakout_down_ext'] = df['close_cloud_breakout_down'] | df['close_cloud_breakout_down'].shift(1)

        # check it ichi_param_4_26 hours ago
        df['lagging_above_cloud'] = np.where(
            ((df.lagging.shift(ichi_displacement) > df.leading_a.shift(ichi_displacement)) &
             (df.lagging.shift(ichi_displacement) > df.leading_b.shift(ichi_displacement))),
            1, 0)
        # shift back to current day
        df['lagging_above_cloud'] = df['lagging_above_cloud'].shift(ichi_displacement)

        df['lagging_below_cloud'] = np.where(
            ((df.lagging.shift(ichi_displacement) < df.leading_a.shift(ichi_displacement)) &
             (df.lagging.shift(ichi_displacement) < df.leading_b.shift(ichi_displacement))),
            1, 0)
        df['lagging_below_cloud'] = df['lagging_below_cloud'].shift(ichi_displacement)


        df['lagging_above_highest'] = np.where(df.lagging.shift(ichi_displacement) > df.high.shift(ichi_displacement), 1, 0)
        df['lagging_above_highest'] = df['lagging_above_highest'].shift(ichi_displacement)

        df['lagging_below_lowest'] = np.where(df.lagging.shift(ichi_displacement) < df.low.shift(ichi_displacement), 1, 0)
        df['lagging_below_lowest'] = df['lagging_below_lowest'].shift(ichi_displacement)

        df['conversion_above_base'] = np.where(df.conversion > df.base, 1, 0)
        df['conversion_below_base'] = np.where(df.conversion < df.base, 1, 0)



        # get the last event line in DF, these are all events together
        last_events = df.iloc[-1]
        time_of_last_row = df.index[-1]
        time_current = pd.to_datetime(kwargs['timestamp'], unit='s')
        #assert (abs(time_current - time_of_last_row).value < 1800000)  # check if difference with now now > 30min
        last_events = last_events.fillna(False)

        # save event in DB and no signal emitting
        for event_name in ICHI_ELEMENTARY_EVENTS:
            event_value = last_events[event_name]
            if event_value:
                logger.debug('   >>> Ichi elem event was FIRED : ' + str(event_name))
                try:
                    ichi_event = cls(
                        **kwargs,
                        event_name=event_name,
                        event_value=int(1),
                    )
                    if MODIFY_DB: ichi_event.save()
                except Exception as e:
                    logger.error(" Error saving  " + event_name + " elementary event ")



        ############## calculate and save ANN Events   #################
        if RUN_ANN:
            logger.info("   ... Check AI Elementary Events: ")
            _process_ai_simple(horizon, **kwargs)





###################
def get_current_elementory_events_df(timestamp, source, transaction_currency, counter_currency, resample_period)->pd.DataFrame:
    '''
    get all elementary events happened in the one timestamp
    NOTE - DB request returns several records for one timestamp!
    '''
    last_events = list(EventsElementary.objects.filter(
        timestamp = timestamp,
        #timestamp__gte=timestamp - timedelta(minutes=(resample_period)).seconds, # for local debug
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        resample_period=resample_period,
    ).order_by('-timestamp').values('timestamp','event_name','event_value'))

    # convert several records into one line of dataFrame
    df = pd.DataFrame()
    if last_events:
        # assert all timestamps are the same
        ts = [rec['timestamp'] for rec in last_events]
        event_names = [rec['event_name'] for rec in last_events]
        event_values = [rec['event_value'] for rec in last_events]

        df = pd.DataFrame(columns = ALL_POSSIBLE_ELEMENTARY_EVENTS, index=pd.Series(ts[0])) # DF has only one line
        df[event_names] = event_values
        df = df.fillna(value=0)

    return df


# the different with the previous one is that it returns the last row in a pile even if it was entered a month ago
def get_last_ever_entered_elementory_events_df(timestamp, source, transaction_currency, counter_currency, resample_period):

    # get the most recent time
    last_time = EventsElementary.objects.filter(
        source=source,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
        resample_period=resample_period,
    ).order_by('-timestamp').values('timestamp').first()

    # convert several records into one line of dataFrame
    df = pd.DataFrame()

    # if there is at least one record and this record is not too far away (not later then 50 hours ago)
    if bool(last_time): # if there is any record
        if (abs(timestamp - last_time['timestamp'].timestamp()) < (3600000 * 50)):
            # get all records for this time
            last_events = list(EventsElementary.objects.filter(
                timestamp=last_time['timestamp'],
                source=source,
                transaction_currency=transaction_currency,
                counter_currency=counter_currency,
                resample_period=resample_period,
            ).order_by('-timestamp').values('timestamp', 'event_name', 'event_value'))

            # assert all timestamps are the same
            ts = [rec['timestamp'] for rec in last_events]
            event_names = [rec['event_name'] for rec in last_events]
            event_values = [rec['event_value'] for rec in last_events]

            df = pd.DataFrame(columns = ALL_POSSIBLE_ELEMENTARY_EVENTS, index=pd.Series(ts[0])) # DF has only one line
            df[event_names] = event_values
            df = df.fillna(value=0)

    return df
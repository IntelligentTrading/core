import datetime
import logging
import time

from django.db import connection

from apps.common.utilities.sqs import send_sqs
from apps.indicator.models.price_resampl import PriceResampl
from apps.indicator.models.rsi import Rsi
from apps.indicator.models.sma import Sma
from apps.strategy.models.strategy_ref import get_all_strategy_classes
from apps.user.models.user import get_horizon_value_from_string
from settings import SHORT, MEDIUM, HORIZONS_TIME2NAMES, RUN_ANN, MODIFY_DB
from taskapp.helpers.common import get_currency_pairs, quad_formatted

# from taskapp.helpers.backtesting import _backtest_all_strategies


logger = logging.getLogger(__name__)


def _compute_ann(source, resample_period):
    '''
    Compute ANN price prediction at each time point in the same way as regular indicators do
    i.e. every short/mediun/long
    '''
    if not RUN_ANN:
        logger.info(" ++++ Running ANN is blocked by settings for debug!  +++++ ")
        return

    # TODO: here we have to load two models for SHORT and pass them
    # from apps.ai.settings.ai_preload import MODELS_PRELOADED
    from apps.ai.models.nn_model import load_all_models
    MODELS_PRELOADED = load_all_models()  # TODO: find a way to cache it!!!

    # TODO: get pairs from def(SOURCE)
    # pairs_to_iterate = [(itm,Price.USDT) for itm in USDT_COINS] + [(itm,Price.BTC) for itm in BTC_COINS]

    pairs_to_iterate = get_currency_pairs(source=source, period_in_seconds=resample_period * 60 * 2)
    # logger.debug("## Pairs to iterate: " + str(pairs_to_iterate))

    timestamp = time.time() // (1 * 60) * (1 * 60)  # rounded to a minute

    for transaction_currency, counter_currency in pairs_to_iterate:
        logger.info('   ======== ANN:: EXCHANGE: ' + str(source) + '| period: ' + str(
            resample_period) + '| checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(
            counter_currency))

        start = time.time()

        # create a dictionary of parameters to improve readability
        indicator_params_dict = {
            'timestamp': timestamp,
            'source': source,
            'transaction_currency': transaction_currency,
            'counter_currency': counter_currency,
            'resample_period': resample_period
        }

        # calculate ANN indicator(s)
        if (resample_period in [SHORT, MEDIUM]):
            from apps.indicator.models.ann_future_price_classification import AnnPriceClassification
            try:
                AnnPriceClassification.compute_all(AnnPriceClassification, MODELS_PRELOADED, **indicator_params_dict)
                logger.info(f"  ... one ANN indicator completed,  ELAPSED Time: {time.time() - start}")
            except Exception as e:
                logger.error(f"ANN Indicator Exception (ANN has not been calculated): {e}")

    end = time.time()
    logger.info(" ALL AI indicators completed:  ELAPSED Time: " + str(end - timestamp))

    # clean session to prevent memory leak
    logger.debug("   ... Cleaning Keras session...")
    from keras import backend as K
    K.clear_session()


def _compute_indicators_for(source, transaction_currency, counter_currency, resample_period):
    logger.info(
        f"### Starting calcs for: {quad_formatted(source, transaction_currency, counter_currency, resample_period)}")

    horizon = get_horizon_value_from_string(display_string=HORIZONS_TIME2NAMES[resample_period])

    timestamp = time.time() // (1 * 60) * (1 * 60)  # current time rounded to a minute

    # create a dictionary of parameters to improve readability
    indicator_params_dict = {
        'timestamp': timestamp,
        'source': source,
        'transaction_currency': transaction_currency,
        'counter_currency': counter_currency,
        'resample_period': resample_period
    }

    # ################# BACK CALCULATION (need only once when run first time)
    # BACK_REC = 5   # how many records to calculate back in time
    # BACK_TIME = timestamp - BACK_REC * resample_period * 60  # same in sec

    # last_time_computed = get_first_resampled_time(source, transaction_currency, counter_currency, resample_period)
    # records_to_compute = int((last_time_computed-BACK_TIME)/(resample_period * 40))

    # if records_to_compute >= 0:
    #     logger.info(f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)}  ... calculate resampl back in time, needed records: {records_to_compute}")
    #     # logger.info("  ... calculate resampl back in time, needed records: " + str(records_to_compute))
    #     for idx in range(1, records_to_compute):
    #         time_point_back = last_time_computed - idx * (resample_period * 60)
    #         # round down to the closest hour
    #         indicator_params_dict['timestamp'] = time_point_back // (60 * 60) * (60 * 60)

    #         try:
    #             resample_object = PriceResampl.objects.create(**indicator_params_dict)
    #             status = resample_object.compute()
    #             if status or (idx == records_to_compute-1): # leave the last empty record
    #                 resample_object.save()
    #             else:
    #                 resample_object.delete()  # delete record if no price was added
    #         except Exception as e:
    #             logger.error(f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} -> Back RESAMPLE EXCEPTION: {e}")
    #             # logger.error(" -> Back RESAMPLE EXCEPTION: " + str(e))

    #     # logger.debug("... resample back  - DONE.")
    #     logger.debug(f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)}... resample back  - DONE.")
    # else:
    #     # logger.debug("   ... No back calculation needed")
    #     logger.debug(f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)}   ... No back calculation needed")

    # # set time back to a current time
    # indicator_params_dict['timestamp'] = timestamp
    # ################# Can be commented after first time run

    # 1 ############################
    # calculate and save resampling price
    # todo - prevent adding an empty record if no value was computed (static method below)
    try:
        resample_object = PriceResampl.objects.create(**indicator_params_dict)
        resample_object.compute()
        if MODIFY_DB: resample_object.save()  # we set MODIFY_DB = False for debug mode, so we can debug with real DB
        # logger.debug("  ... Resampled completed,  ELAPSED Time: " + str(time.time() - timestamp))
        logger.debug(
            f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} ... Resampled completed,  ELAPSED Time: {time.time() - timestamp}")
    except Exception as e:
        # logger.error(" -> RESAMPLE EXCEPTION: " + str(e))
        logger.error(
            f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} -> RESAMPLE EXCEPTION: {e}")



    # 2 ###########################
    # calculate and save simple indicators
    indicators_list = [Sma, Rsi]
    for ind in indicators_list:
        try:
            ind.compute_all(ind, **indicator_params_dict)
            # logger.debug("  ... Regular indicators completed,  ELAPSED Time: " + str(time.time() - timestamp))
            logger.debug(
                f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} ... Regular indicators completed,  ELAPSED Time: {time.time() - timestamp}")
        except Exception as e:
            # logger.error(str(ind) + " Indicator Exception: " + str(e))
            logger.error(
                f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} {(ind)} Indicator Exception: {e}")

    # 4 #############################
    # check for events and save if any
    from apps.indicator.models.events_elementary import EventsElementary
    from apps.indicator.models.events_logical import EventsLogical
    for event in [EventsElementary, EventsLogical]:
        try:
            event.check_events(event, **indicator_params_dict)
            # logger.debug("  ... Events completed,  ELAPSED Time: " + str(time.time() - timestamp))
            logger.debug(
                f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)}  ... Events completed,  ELAPSED Time: {time.time() - timestamp}")
        except Exception as e:
            # logger.error(" Event Exception: " + str(e))
            logger.error(
                f">>>>{quad_formatted(source, transaction_currency, counter_currency, resample_period)} Event Exception: {e}")

        logger.debug("|| SQL for Events: helpers.indicators._compute_indicators, events || " + str(connection.queries))

    # 5 ############################
    # TODO: Uncomment when strategies are ready, it will emit strategy signals
    # check if we have to emit any <Strategy> signals

    strategies_list = get_all_strategy_classes()  # [RsiSimpleStrategy, SmaCrossOverStrategy]

    for strategy in strategies_list:
        try:
            s = strategy(**indicator_params_dict)
            now_signals_set = s.check_signals_now()

            if now_signals_set:
                logger.debug(
                    "  NOW: found Signal belongs to strategy : " + str(strategy) + " : " + str(now_signals_set))

                # Emit to a signal from a strategy to sqs without saving it in the Signal table
                # combine a dictionary with all data
                dict_to_emit = {
                    "id": hex(int(time.time() * 10000000))[2:],
                    **indicator_params_dict,
                    "horizon": horizon,
                    "strategy": str(s),
                    "signal_name": now_signals_set  # str(now_signals_set)
                    # TODO @Alex check and fix if needed
                }
                dict_to_emit['timestamp'] = datetime.datetime.utcfromtimestamp(dict_to_emit['timestamp']).strftime(
                    '%Y-%m-%d %H:%M:%S')
                send_sqs(dict_to_emit)
            else:
                logger.debug("   ... No STRATEGY signals has been found NOW.")
        except Exception as e:
            logger.error(f" Error Strategy checking:  {e}")

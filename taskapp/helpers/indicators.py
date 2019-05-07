import logging
import time

from django.db import connection

from apps.common.utilities.sqs import send_sqs
from apps.indicator.models.price_resampl import PriceResampl
from apps.indicator.models.rsi import Rsi
from apps.indicator.models.sma import Sma
from apps.user.models.user import get_horizon_value_from_string
from settings import SHORT, MEDIUM, HORIZONS_TIME2NAMES, MODIFY_DB
from taskapp.helpers.common import get_tickers, quad_formatted

logger = logging.getLogger(__name__)


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

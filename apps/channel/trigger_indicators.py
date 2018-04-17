import time
import logging

from apps.indicator.models import Price, Volume
from apps.indicator.models.price_resampl import get_n_last_resampl_df, get_first_resampled_time

from settings import USDT_COINS, BTC_COINS
from settings import PERIODS_LIST, SHORT, MEDIUM, LONG

logger = logging.getLogger(__name__)


def compute_and_save_indicators(**kwargs):
    from apps.indicator.models.price_resampl import PriceResampl
    from apps.indicator.models.sma import Sma
    from apps.indicator.models.rsi import Rsi
    from apps.indicator.models.events_elementary import EventsElementary
    from apps.indicator.models.events_logical import EventsLogical

    timestamp = time.time()
    resample_period = kwargs['period']
    channel = kwargs['channel']

    logger.debug(" ################# Resampling with Period: " + str(resample_period) + " #######################")

    pairs_to_iterate = [(itm,Price.USDT) for itm in USDT_COINS] + [(itm,Price.BTC) for itm in BTC_COINS]
    for transaction_currency, counter_currency in pairs_to_iterate:

        logger.debug('   ======== checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(counter_currency))

        # create a dictionary of parameters to improve readability
        indicator_params_dict = {
            'timestamp' : timestamp,
            'source' : channel,
            'transaction_currency' : transaction_currency,
            'counter_currency' : counter_currency,
            'resample_period' : resample_period
        }
        ################# BACK CALCULATION (need only once when run first time)
        BACK_REC = 210   # how many records to calculate back in time
        BACK_TIME = timestamp - BACK_REC * resample_period * 60  # same in sec

        last_time_computed = get_first_resampled_time(channel, transaction_currency, counter_currency, resample_period)
        records_to_compute = int((last_time_computed-BACK_TIME)/(resample_period * 60))

        if records_to_compute >= 0:
            logger.debug("  ... calculate resampl back in time, needed records: " + str(records_to_compute))
            for idx in range(1, records_to_compute):
                time_point_back = last_time_computed - idx * (resample_period * 60)
                indicator_params_dict['timestamp'] = time_point_back
                try:
                    resample_object = PriceResampl.objects.create(**indicator_params_dict)
                    status = resample_object.compute()
                    if status or (idx == records_to_compute-1) : # leave the last empty record
                        resample_object.save()
                    else:
                        resample_object.delete()  # delete record if no price was added
                except Exception as e:
                    logger.error(" -> Back RESAMPLE EXCEPTION: " + str(e))
            logger.debug("... resample back  - DONE.")
        else:
            logger.debug("   ... No back calculation needed")

        # set time back to a current time
        indicator_params_dict['timestamp'] = timestamp

        ################# Can be commented after first time run

        # calculate and save resampling price
        # todo - prevent adding an empty record if no value was computed (static method below)
        try:
            resample_object = PriceResampl.objects.create(**indicator_params_dict)
            resample_object.compute()
            resample_object.save()
        except Exception as e:
            logger.error(" -> RESAMPLE EXCEPTION: " + str(e))

        # calculate and save simple indicators
        indicators_list = [Sma, Rsi]
        for ind in indicators_list:
            try:
                ind.compute_all(ind, **indicator_params_dict)
            except Exception as e:
                logger.error(str(ind) + " Indicator Exception: " + str(e))

        # check for events and save if any
        # todo: make sure EventsElementary runs first

        events_list = [EventsElementary, EventsLogical]
        for event in events_list:
            try:
                event.check_events(event, **indicator_params_dict)
            except Exception as e:
                logger.error("Event Exception: " + str(e))




import json
import logging
import time
import sys

from django.core.management.base import BaseCommand
from requests import get, RequestException

from apps.channel.models import ExchangeData
from apps.channel.models.exchange_data import POLONIEX
from apps.indicator.models import Price, Volume
from apps.indicator.models.price import get_currency_value_from_string, get_n_last_prices_ts
from apps.indicator.models.price_resampl import get_first_resampled_time
from apps.indicator.models.volume import get_n_last_volumes_ts

from apps.indicator.models.price_resampl import PriceResampl
from apps.indicator.models.sma import Sma
from apps.indicator.models.rsi import Rsi
from apps.indicator.models.events_elementary import EventsElementary
from apps.indicator.models.events_logical import EventsLogical
from keras.models import load_model

from settings import time_speed  # 1 / 10
from settings import USDT_COINS, BTC_COINS
from settings import PERIODS_LIST, SHORT, MEDIUM, LONG

import pandas as pd
import numpy as np



logger = logging.getLogger(__name__)

def _pull_poloniex_data():
    logger.info("pulling Poloniex data...")
    req = get('https://poloniex.com/public?command=returnTicker')

    data = req.json()
    timestamp = time.time()

    poloniex_data_point = ExchangeData.objects.create(
        source=POLONIEX,
        data=json.dumps(data),
        timestamp=timestamp
    )
    logger.info("Saving Poloniex price, volume data...")
    _save_prices_and_volumes(data, timestamp)


def _save_prices_and_volumes(data, timestamp):
    for currency_pair in data:
        try:
            counter_currency_string = currency_pair.split('_')[0]
            counter_currency = get_currency_value_from_string(counter_currency_string)
            assert counter_currency >= 0
            transaction_currency_string = currency_pair.split('_')[1]
            assert len(transaction_currency_string) > 1 and len(transaction_currency_string) <= 6

            Price.objects.create(
                source=POLONIEX,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                price=int(float(data[currency_pair]['last']) * 10 ** 8),
                timestamp=timestamp
            )

            Volume.objects.create(
                source=POLONIEX,
                transaction_currency=transaction_currency_string,
                counter_currency=counter_currency,
                volume=float(data[currency_pair]['baseVolume']),
                timestamp=timestamp
            )
        except Exception as e:
            logger.debug(str(e))

    logger.debug("Saved Poloniex price and volume data")


def _compute_and_save_indicators(resample_period_par):

    try:
        model_path = sys.path[0] + '/apps/indicator/models/lstm_model.h5'
        model = load_model(model_path)
    except Exception as e:
        logger.error(" >>> Canot load KERAS model " + str(e))


    timestamp = time.time() // (1 * 60) * (1 * 60)   # rounded to a minute
    resample_period = resample_period_par['period']

    logger.info(" ################# Resampling with Period: " + str(resample_period) + " #######################")

    pairs_to_iterate = [(itm,Price.USDT) for itm in USDT_COINS] + [(itm,Price.BTC) for itm in BTC_COINS]

    for transaction_currency, counter_currency in pairs_to_iterate:
        logger.info('   ======== ' + str(resample_period)+ ': checking COIN: ' + str(transaction_currency) + ' with BASE_COIN: ' + str(counter_currency))

        # create a dictionary of parameters to improve readability
        indicator_params_dict = {
            'timestamp': timestamp,
            'source': POLONIEX,
            'transaction_currency': transaction_currency,
            'counter_currency': counter_currency,
            'resample_period': resample_period
        }

        ################# BACK CALCULATION (need only once when run first time)
        BACK_REC = 310   # how many records to calculate back in time
        BACK_TIME = timestamp - BACK_REC * resample_period * 60  # same in sec

        last_time_computed = get_first_resampled_time(POLONIEX, transaction_currency, counter_currency, resample_period)
        records_to_compute = int((last_time_computed-BACK_TIME)/(resample_period * 60))

        if records_to_compute >= 0:
            logger.info("  ... calculate resampl back in time, needed records: " + str(records_to_compute))
            for idx in range(1, records_to_compute):
                time_point_back = last_time_computed - idx * (resample_period * 60)
                # round down to the closest hour
                indicator_params_dict['timestamp'] = time_point_back // (60 * 60) * (60 * 60)

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


        ############################ check feasibility of keras and tensor flow on Heroku
        try:
            res_period = '10min'
            win_size = 200
            needed_records = win_size * 11

            raw_price_ts = get_n_last_prices_ts(needed_records, indicator_params_dict['source'], transaction_currency, counter_currency)
            raw_volume_ts = get_n_last_volumes_ts(needed_records, indicator_params_dict['source'], transaction_currency, counter_currency)

            raw_data_frame = pd.merge(raw_price_ts.to_frame(name='price'), raw_volume_ts.to_frame(name='volume'), how='left', left_index=True, right_index=True)
            raw_data_frame[pd.isnull(raw_data_frame)] = None

            data_ts = raw_data_frame.resample(rule=res_period).mean()
            data_ts['price_var'] = raw_data_frame['price'].resample(rule=res_period).var()
            data_ts['volume_var'] = raw_data_frame['volume'].resample(rule=res_period).var()
            data_ts = data_ts.interpolate()
            data_ts = data_ts.tail(win_size)
            assert len(data_ts) == win_size, ' :: Wrong training example lenght!'

            # data (124451, 196, 4) : 4 = price/volume/price_var/volume_var
            X_test = np.zeros([1,win_size,4])
            X_test[0, :, 0] = data_ts['price']
            X_test[0, :, 1] = data_ts['volume']
            X_test[0, :, 2] = data_ts['price_var']
            X_test[0, :, 3] = data_ts['volume_var']

            for example in range(X_test.shape[0]):
                X_test[example, :, 0] = (X_test[example, :, 0] - X_test[example, -1, 0]) / (np.max(X_test[example, :, 0]) - np.min(X_test[example, :, 0]))
                X_test[example, :, 1] = (X_test[example, :, 1] - X_test[example, -1, 1]) / (np.max(X_test[example, :, 1]) - np.min(X_test[example, :, 1]))
                X_test[example, :, 2] = (X_test[example, :, 2] - X_test[example, -1, 2]) / (np.max(X_test[example, :, 2]) - np.min(X_test[example, :, 2]))
                X_test[example, :, 3] = (X_test[example, :, 3] - X_test[example, -1, 3]) / (np.max(X_test[example, :, 3]) - np.min(X_test[example, :, 3]))

            # check for NaN


            # check if keras and tensor flow are workging from Heroku
            logger.debug('@@@@@@    Prepare to run Keras     @@@@@@@@@')


            # data (124451, 196, 4) : 4 = price/volume/price_var/volume_var
            trend_predicted = model.predict(X_test)

            logger.debug('>>> AI EMITS <<< Predicted next trend probabilities (same/up/down): ' + str(trend_predicted))
        except Exception as e:
            logger.error(">> AI chek up error: probably keras or tensorflow do not work :(  |  " + str(e))

        ##############################
        # check for events and save if any
        events_list = [EventsElementary, EventsLogical]
        for event in events_list:
            try:
                event.check_events(event, **indicator_params_dict)
            except Exception as e:
                logger.error("Event Exception: " + str(e))

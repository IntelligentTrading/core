import time
import pandas as pd
import numpy as np

from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.ai.models.nn_model import AnnModel
from apps.indicator.models.price import get_n_last_prices_ts
from apps.indicator.models.volume import get_n_last_volumes_ts

import logging
logger = logging.getLogger(__name__)


class AnnPriceClassification(AbstractIndicator):
    ann_model = models.ForeignKey(AnnModel, on_delete=models.CASCADE)

    predicted_ahead_for = models.SmallIntegerField(null=True) # in mins
    probability_same = models.FloatField(null=True)
    probability_up = models.FloatField(null=True)
    probability_down = models.FloatField(null=True)

    @staticmethod
    def compute_all(cls, ann_model, **kwargs):
        logger.debug('@@@@@@    Run AI prediction    @@@@@@@@@')

        start = time.time()

        trend_predicted = _compute_lstm_classification(ann_model, **kwargs)

        # create a record is we have predicted values
        if trend_predicted:
            new_instance = cls.objects.create(
                **kwargs,
                ann_model=ann_model,
                predicted_ahead_for = ann_model.predicted_win_size,  # in mins, can remove we also have it in ann model
                probability_same = trend_predicted[0],
                probability_up = trend_predicted[1],
                probability_down = trend_predicted[2]
            )
            new_instance.save()
            logger.info("   ...LSTM prediction has been calculated and saved.")
        else:
            logger.info(" ... No predicted probabilities have been returned")

        end = time.time()
        logger.debug(" @@@@@@   End of running AI.  ELAPSED Time: " + str(end - start))



def _compute_lstm_classification(ann_model, **kwargs):
    trend_predicted = None

    resample_period = str(ann_model.period) + 'min'  #'10min'
    needed_records = ann_model.slide_win_size * 11  # because of 10min

    # get raw prices from Price table to form a feature vector to feed up to ANN (to predict price)
    raw_price_ts = get_n_last_prices_ts(needed_records, kwargs['source'], kwargs['transaction_currency'], kwargs['counter_currency'])
    raw_volume_ts = get_n_last_volumes_ts(needed_records, kwargs['source'], kwargs['transaction_currency'], kwargs['counter_currency'])

    raw_data_frame = pd.merge(raw_price_ts.to_frame(name='price'), raw_volume_ts.to_frame(name='volume'), how='left', left_index=True, right_index=True)
    raw_data_frame[pd.isnull(raw_data_frame)] = None

    # resample (might be different from our standart values 60/240/1440
    # calculate additional features (variance)
    data_ts = raw_data_frame.resample(rule=resample_period).mean()
    data_ts['price_var'] = raw_data_frame['price'].resample(rule=resample_period).var()
    data_ts['volume_var'] = raw_data_frame['volume'].resample(rule=resample_period).var()
    data_ts = data_ts.interpolate()
    # get only reacent time points according to trained model
    data_ts = data_ts.tail(ann_model.slide_win_size)
    logger.debug('lenght of one training example is ' + str(len(data_ts)) )
    assert len(data_ts) == ann_model.slide_win_size, ' @@@@@ :: Wrong training example lenght!'

    # combine the data into X matrix like that
    # (examples=124451, features=196, classes=4) : 4 = price/volume/price_var/volume_var
    X_test = np.zeros([1, ann_model.slide_win_size,4])
    X_test[0, :, 0] = data_ts['price']
    X_test[0, :, 1] = data_ts['volume']
    X_test[0, :, 2] = data_ts['price_var']
    X_test[0, :, 3] = data_ts['volume_var']

    # Normalize data so that it ends in curent price value and btw -1 / 1
    for example in range(X_test.shape[0]):
        X_test[example, :, 0] = (X_test[example, :, 0] - X_test[example, -1, 0]) / (np.max(X_test[example, :, 0]) - np.min(X_test[example, :, 0]))
        X_test[example, :, 1] = (X_test[example, :, 1] - X_test[example, -1, 1]) / (np.max(X_test[example, :, 1]) - np.min(X_test[example, :, 1]))
        X_test[example, :, 2] = (X_test[example, :, 2] - X_test[example, -1, 2]) / (np.max(X_test[example, :, 2]) - np.min(X_test[example, :, 2]))
        X_test[example, :, 3] = (X_test[example, :, 3] - X_test[example, -1, 3]) / (np.max(X_test[example, :, 3]) - np.min(X_test[example, :, 3]))

    # TODO: it looks liek we cannot store Keras model as an object in class
    # check if I can load the model here or do a batch predictionat the end for all currencies

    # run prediction
    if ann_model.keras_model :
        trend_predicted = ann_model.keras_model.predict(X_test)
        logger.debug('>>> AI <<< Predicted probabilities for price for next period, (same/up/down): ' + str(trend_predicted))
    else:
        logger.debug(">> Model does not exists! ")

    if np.isnan(trend_predicted).all():
        return None
    else:
        return trend_predicted







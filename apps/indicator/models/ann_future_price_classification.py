'''
@AlexY :
NOTE: before using AI prediction a AI model must be manually added as follows
 - upload a model to S3
 - run a django command      python manage.py add_nn_model

'''
import time
from datetime import timedelta, datetime
import pandas as pd
import numpy as np

from django.db import models
#from django.db import connection
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.ai.models.nn_model import AnnModel
from apps.indicator.models.price_history import get_n_last_prices_ts, get_n_last_volumes_ts
#from apps.indicator.models.ann_future_price_classification import AnnPriceClassification
from settings import MODIFY_DB
from apps.ai.models.nn_model import MODEL_REF

import logging
logger = logging.getLogger(__name__)

#MODEL_LIST = ["PRICE_PREDICT", "PRICE_MAXHIT"] # , "PRICE_MINHIT"


class AnnPriceClassification(AbstractIndicator):
    '''
    Every period this class gives a prediction for the future whether the price will go up or down
    In essence it is one more indicator same as RSI, SMA, which givev a continuous prediction for every coin
    '''
    ann_model = models.ForeignKey(AnnModel, on_delete=models.CASCADE)  # a version of model which made the prediction

    #TODO: add a model type: AnnSImple / ANN MAX HIY
    # in the future remove th FK to ann_model

    # PRICE_PREDICT / PRICE_MAXHIT / PRICE_MINHIT
    ai_model = models.CharField(max_length=16, null=True, blank=True)

    predicted_ahead_for = models.SmallIntegerField(null=True) # in mins, price predicted for this time frame
    probability_same = models.FloatField(null=True)  # probability of price will stay the same
    probability_up = models.FloatField(null=True)
    probability_down = models.FloatField(null=True)

    @property
    def get_max_prob_same_up_down(self):
        return np.argmax([self.probability_same, self.probability_up, self.probability_down])

    @property
    def get_max_prob_up_down(self):
        # add one to shift the number, up must be 1, not zero
        return np.argmax([self.probability_up, self.probability_down]) + 1


    @staticmethod
    def compute_all(cls, models_preloaded, **kwargs):

        resample_period = kwargs['resample_period']
        MODEL_LIST = [x[0] for x in MODEL_REF.keys() if x[1]==resample_period]  # get only models loaded to S3

        start = time.time()
        for model in MODEL_LIST:
            logger.info('   @@@@@@    Run AI indicator calculation  with %s model   @@@@@@@@@' % (model))

            # load model from S3 and database
            #ann_model_object = get_ann_model_object(period2model[resample_period][model])

            ann_model_object = models_preloaded[(model,resample_period)]

            # run prediction
            trend_predicted = _compute_lstm_classification(ann_model_object, **kwargs)

            # create a record if we have predicted values
            if trend_predicted is not None:
                new_instance = cls(  #cls.objects.create( <- we do "save" separatelly now
                    **kwargs,
                    ann_model=ann_model_object, #FK
                    ai_model=model[:15],
                    predicted_ahead_for = ann_model_object.predicted_win_size * ann_model_object.period,  # in mins, can remove we also have it in ann model
                    probability_same = trend_predicted[0],
                    probability_up = trend_predicted[1],
                    probability_down=trend_predicted[2] if len(trend_predicted)==3 else None,
                )
                if MODIFY_DB: new_instance.save()
                logger.info("   ...LSTM prediction indicator has been calculated and saved.")
            else:
                logger.info(" ... No predicted probabilities have been returned")

        end = time.time()

        logger.info("   @@@@@@   End of running AI indicator.  ELAPSED Time: " + str(end - start))



def _compute_lstm_classification(ann_model, **kwargs):

    # resample_period = str(ann_model.period) + 'min'  #'10min'
    # needed_records = ann_model.slide_win_size * ann_model.period + 10  # because of 10min/60 min + some extra
    #
    # # get raw prices from Price table to form a feature vector to feed up to ANN (to predict price)
    # raw_price_ts = get_n_last_prices_ts(needed_records, kwargs['source'], kwargs['transaction_currency'], kwargs['counter_currency'])
    # raw_volume_ts = get_n_last_volumes_ts(needed_records, kwargs['source'], kwargs['transaction_currency'], kwargs['counter_currency'])
    #
    # raw_data_frame = pd.merge(raw_price_ts.to_frame(name='price'), raw_volume_ts.to_frame(name='volume'), how='left', left_index=True, right_index=True)
    # raw_data_frame[pd.isnull(raw_data_frame)] = None
    #
    # # resample (might be different from our standart values 60/240/1440
    # # calculate additional features (variance)
    # data_ts = raw_data_frame.resample(rule=resample_period).mean()
    # data_ts['price_var'] = raw_data_frame['price'].resample(rule=resample_period).var()
    # data_ts['volume_var'] = raw_data_frame['volume'].resample(rule=resample_period).var()
    # data_ts = data_ts.interpolate()
    #
    # # get only recent time points according to trained model
    # data_ts = data_ts.tail(ann_model.slide_win_size)
    # logger.debug('   ... length of one feature vector to predict on is ' + str(len(data_ts)) )
    # assert len(data_ts) == ann_model.slide_win_size, ' @@@@@ :: Wrong training example length!'

    data_ts = ann_model.get_dataset(**kwargs)

    # combine the data into X matrix like that
    # (examples=124451, features=196, classes=4) : 4 = price/volume/price_var/volume_var
    X_predict = np.zeros([1, ann_model.slide_win_size,4])
    X_predict[0, :, 0] = data_ts['price']
    X_predict[0, :, 1] = data_ts['volume']
    X_predict[0, :, 2] = data_ts['price_var']
    X_predict[0, :, 3] = data_ts['volume_var']

    # check if we have Nans
    # TODO: interpolate or cancel calculation if yes (CLEANING input data)
    # TODO: download price and VOLUME tables too!
    logger.debug("    ... Do we have NaNs in X?: " + str(np.isnan(X_predict[0, :, :]).any()))

    if sum(sum(np.isnan(X_predict[0, :, :]))) > 40:
        logger.info(" >> Cancel AI prediction, because too many NaNs, prediction is not reliable!")
        return None


    # Normalize data so that it ends in curent price value and btw -1 / 1
    for example in range(X_predict.shape[0]):
        X_predict[example, :, 0] = (X_predict[example, :, 0] - X_predict[example, -1, 0]) / (np.max(X_predict[example, :, 0]) - np.min(X_predict[example, :, 0]))
        X_predict[example, :, 1] = (X_predict[example, :, 1] - X_predict[example, -1, 1]) / (np.max(X_predict[example, :, 1]) - np.min(X_predict[example, :, 1]))
        X_predict[example, :, 2] = (X_predict[example, :, 2] - X_predict[example, -1, 2]) / (np.max(X_predict[example, :, 2]) - np.min(X_predict[example, :, 2]))
        X_predict[example, :, 3] = (X_predict[example, :, 3] - X_predict[example, -1, 3]) / (np.max(X_predict[example, :, 3]) - np.min(X_predict[example, :, 3]))

    # TODO: it looks like we cannot store Keras model as an object in class
    # check if I can load the model here or do a batch predictionat the end for all currencies

    # run prediction
    trend_predicted = None
    if ann_model.keras_model :
        loaded_model = ann_model.keras_model
        #logger.info(loaded_model.summary())
        trend_predicted = loaded_model.predict(X_predict)
        logger.debug('>>> AI <<< Predicted probabilities for price for next period, (same/up/down): ' + str(trend_predicted))
    else:
        logger.debug(">> Model does not exists! ")

    if np.isnan(trend_predicted).all():
        return None
    else:
        return trend_predicted[0]  # it is array of arrays because usually the prediction is dome for many rows



def get_n_last_ann_classif_df(n, model_name, **kwargs) ->pd.DataFrame:

    last_records = list(AnnPriceClassification.objects.filter(
        ai_model=model_name,
        source=kwargs['source'],
        resample_period=kwargs['resample_period'],
        transaction_currency=kwargs['transaction_currency'],
        counter_currency=kwargs['counter_currency'],
        timestamp__gte = datetime.now() - timedelta(minutes=kwargs['resample_period'] * n)
    ).values('timestamp', 'probability_same', 'probability_up', 'probability_down','predicted_ahead_for').order_by('timestamp'))

    df = pd.DataFrame()
    if last_records:
        # todo - reverse order or make sure I get values in the same order!
        ts = [rec['timestamp'] for rec in last_records]
        probability_same = pd.Series(data=[rec['probability_same'] for rec in last_records], index=ts)
        probability_up = pd.Series(data=[rec['probability_up'] for rec in last_records], index=ts)
        probability_down = pd.Series(data=[rec['probability_down'] for rec in last_records], index=ts)
        predicted_ahead_for = pd.Series(data=[rec['predicted_ahead_for'] for rec in last_records], index=ts)

        df['probability_same'] = probability_same
        df['probability_up'] = probability_up
        df['probability_down'] = probability_down
        df['predicted_ahead_for'] = predicted_ahead_for
    else:
        logger.error("   !!!!! No recently generated AI events found!")

        # TODO: make sure the last data is at the bottom pf the dataset!

    return df



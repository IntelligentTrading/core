import logging
import time
import pandas as pd
from django.db import models

from apps.indicator.models.price_history import get_n_last_prices_ts, get_n_last_volumes_ts
from apps.indicator.models.price_resampl import get_n_last_resampl_df
from unixtimestampfield.fields import UnixTimeStampField
from apps.common.utilities.s3 import download_file_from_s3
from settings import RUN_ANN, SOURCE_CHOICES

logger = logging.getLogger(__name__)

if RUN_ANN:
    from keras.models import load_model


# AnnModel is a not very smart way to store all keras models we have in the system
# we can load the model by 's3_model_file'
# TODO: remove storing it in DB and keep all models in named dictionary?


class AnnModel(models.Model):
    '''
    Keep all NN models in a database table, so we can keep track of which indicator value
    was calculated with which NN model and be able to reproduce it
    '''

    timestamp = UnixTimeStampField(null=False)
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    model_name = models.CharField(max_length=32, null=False, blank=False)
    s3_model_file = models.TextField(null=False, blank=False)
    s3_notebook_file = models.TextField(null=True)

    period = models.PositiveSmallIntegerField(null=False, blank=False) # 10min, we use full price table, not resampled
    slide_win_size = models.SmallIntegerField(null=False, blank=False)
    predicted_win_size = models.SmallIntegerField(null=False, blank=False)
    delta_tolerance = models.FloatField(null=False)

    train_accuracy = models.FloatField(null=True)
    train_f1_score = models.FloatField(null=True)
    validation_accuracy = models.FloatField(null=True)
    validation_f1_score = models.FloatField(null=True)

    train_data_description = models.TextField(null=True, blank=True)
    features_description = models.TextField(null=True, blank=True)

    keras_model = None

    # download keras model from s3 into keras model
    def initialize(self):
        logger.debug(" >> Start Loading Keras Model..." + self.s3_model_file)
        if self.keras_model:
            logger.debug(" >> KERAS model exists and returned !")
            return self.keras_model
        else:
            download_file_from_s3(self.s3_model_file)
            self.keras_model = load_model(self.s3_model_file) # 'lstm_model.h5'
            logger.debug(" >> KERAS model loaded and returned!")
            return self.keras_model

    # retrieve an appropriate dataset for a given model_type
    def get_dataset(self, **kwargs):
        if self.model_name == "PRICE_PREDICT":
            ''' in case of PRICE_PREDICT we use 1min price and then do resampling
            '''
            resample_period = str(self.period) + 'min'  # '10min'

            needed_records = self.slide_win_size * self.period + 10  # because of 10min/60 min + some extra

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


        if self.model_name == "PRICE_MAXHIT":
            needed_records = self.slide_win_size + 2
            raw_data_frame = get_n_last_resampl_df(
                needed_records, kwargs['source'], kwargs['transaction_currency'], kwargs['counter_currency'], kwargs['resample_period']
            )

            raw_data_frame[pd.isnull(raw_data_frame)] = None
            data_ts['price'] = raw_data_frame['close_price']
            data_ts['volume'] = raw_data_frame['close_volume']
            data_ts['price_max'] = raw_data_frame['high_price']
            data_ts['price_min'] = raw_data_frame['low_price']
            data_ts['price_var'] = raw_data_frame['price_variance']
            data_ts['volume_var'] = raw_data_frame['volume_variance']
            data_ts = data_ts.interpolate()


        # FINALLY: get only recent time points according to trained model
        data_ts = data_ts.tail(self.slide_win_size)
        logger.debug('   ... length of one feature vector to predict on is ' + str(len(data_ts)))
        assert len(data_ts) == self.slide_win_size, ' @@@@@ :: Wrong training example length!'

        return data_ts


# download model file from s3 to local then import it into keras model, then return this keras model
def lookup_ann_model_object(s3_model_file):
    start = time.time()

    ann_model = AnnModel.objects.get(s3_model_file=s3_model_file) ## get ann model metainfo from DB(django objects.get)

    if not ann_model.keras_model:
        try:
            ann_model.initialize()   # download model from S3, save it on local disk, then upload to class
            logger.info(">> ANN model loaded FIRST TIME, ELapsed time: " + str(time.time() - start) + s3_model_file)
        except Exception as e:
            logger.error(" Cannot load ANN model: either no Model in DB or S3 file does not exist")
    else:
        logger.info(">> get ANN model from CACHE, elapsed time: " + str(time.time() - start))

    return ann_model




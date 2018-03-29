import logging
from django.db import models
from apps.channel.models.exchange_data import SOURCE_CHOICES
from unixtimestampfield.fields import UnixTimeStampField
from apps.common.utilities.s3 import download_file_from_s3

from keras.models import load_model

logger = logging.getLogger(__name__)

# redo it as here
# https://www.b-list.org/weblog/2006/aug/18/django-tips-using-properties-models-and-managers/


class AnnModel(models.Model):
    '''
    Save all NN models in a database table, so we can kkep track which indicator value
    was calculated with which NN model
    '''

    timestamp = UnixTimeStampField(null=False)
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, null=False)
    model_name = models.CharField(max_length=32, null=False, blank=False)
    s3_file = models.TextField(null=False, blank=False)
    period = models.PositiveSmallIntegerField(null=False, blank=False) # 10min

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
        if self.keras_model:
            logger.debug(" >> KERAS model exists and returned !")
            return self.keras_model
        else:
            download_file_from_s3(self.s3_file)
            self.keras_model = load_model('lstm_model.h5')
            logger.debug(" >> KERAS model loaded and returned!")
            return self.keras_model


# download model file from s3 to local then import it into keras model, then return this keras model
def get_ann_model(s3_file):
    ann_model = AnnModel.objects.filter(s3_file = s3_file)

    return ann_model.initialize()




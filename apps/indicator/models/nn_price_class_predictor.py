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

    predicted_ahead_for = models.SmallIntegerField(null=False, blank=False) # in mins
    probability_same = models.FloatField(null=True)
    probability_up = models.FloatField(null=True)
    probability_down = models.FloatField(null=True)


    def _compute_lstm_classification(self):

        try:
            start = time.time()
            # check if keras and tensor flow are workging from Heroku
            logger.debug('@@@@@@    Prepare to run AI prediction    @@@@@@@@@')

            resample_period = str(self.ann_model.period) + 'min'  #'10min'

            needed_records = self.ann_model.slide_win_size * 11  # because of 10min

            raw_price_ts = get_n_last_prices_ts(needed_records, self.source, self.transaction_currency, self.counter_currency)
            raw_volume_ts = get_n_last_volumes_ts(needed_records, self.source, self.transaction_currency, self.counter_currency)

            raw_data_frame = pd.merge(raw_price_ts.to_frame(name='price'), raw_volume_ts.to_frame(name='volume'), how='left', left_index=True, right_index=True)
            raw_data_frame[pd.isnull(raw_data_frame)] = None

            data_ts = raw_data_frame.resample(rule=resample_period).mean()
            data_ts['price_var'] = raw_data_frame['price'].resample(rule=resample_period).var()
            data_ts['volume_var'] = raw_data_frame['volume'].resample(rule=resample_period).var()
            data_ts = data_ts.interpolate()
            data_ts = data_ts.tail(self.ann_model.slide_win_size)
            logger.debug('lenght of one training example is ' + str(len(data_ts)) )
            assert len(data_ts) == self.ann_model.slide_win_size, ' :: Wrong training example lenght!'

            # data (124451, 196, 4) : 4 = price/volume/price_var/volume_var
            X_test = np.zeros([1,self.ann_model.slide_win_size,4])
            X_test[0, :, 0] = data_ts['price']
            X_test[0, :, 1] = data_ts['volume']
            X_test[0, :, 2] = data_ts['price_var']
            X_test[0, :, 3] = data_ts['volume_var']

            for example in range(X_test.shape[0]):
                X_test[example, :, 0] = (X_test[example, :, 0] - X_test[example, -1, 0]) / (np.max(X_test[example, :, 0]) - np.min(X_test[example, :, 0]))
                X_test[example, :, 1] = (X_test[example, :, 1] - X_test[example, -1, 1]) / (np.max(X_test[example, :, 1]) - np.min(X_test[example, :, 1]))
                X_test[example, :, 2] = (X_test[example, :, 2] - X_test[example, -1, 2]) / (np.max(X_test[example, :, 2]) - np.min(X_test[example, :, 2]))
                X_test[example, :, 3] = (X_test[example, :, 3] - X_test[example, -1, 3]) / (np.max(X_test[example, :, 3]) - np.min(X_test[example, :, 3]))


            # data (124451, 196, 4) : 4 = price/volume/price_var/volume_var
            if self.ann_model.keras_model :
                trend_predicted = self.ann_model.keras_model.predict(X_test)
                logger.debug('>>> AI EMITS <<< Predicted probabilities for price for next 15 hours, (same/up/down): ' + str(trend_predicted))
            else:
                logger.debug(">> Model does not exists! ")

            end = time.time()
            logger.debug(" ELAPSED Time of AI prediction: " + str(end - start))

            # TODO: add a AnnPriceClassification object creation

        except Exception as e:
            logger.error(">> AI prediction error  |  " + str(e))

        logger.debug('@@@@@@   End of running AI  @@@@@@@')


    @staticmethod
    def compute_all(cls, ann_model, **kwargs):
        new_instance = cls.objects.create(
            ann_model=ann_model
        )
        new_instance._compute_lstm_classification()
        new_instance.save()
        logger.info("   ...LSTM prediction has been calculated and saved.")
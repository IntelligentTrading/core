import logging
import time
from django.core.management.base import BaseCommand
from apps.ai.models.nn_model import AnnModel
from apps.channel.models.exchange_data import POLONIEX

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    Run this command if you need to add a new NN model
    Keras or TF model must be already uploaded to S3
    '''
    help = 'Add a new NN model to a database '

    def handle(self, *args, **options):
        logger.info("Adding a new Neural Network model to a database")

        # check if it exists
        # TODO: add automatic import from S3 + command line questionaaire about text fields + may be link to Notebook

        if not AnnModel.objects.filter(s3_file = 'lstm_model_2_2.h5').exists():
            AnnModel.objects.create(
                timestamp=time.time(),
                source = POLONIEX,
                model_name = 'LSTM',
                s3_model_file = 'lstm_model_2_2.h5',
                s3_notebook_file = '04_ML_Keras_LSTM_Three_Class_ALLCOINS_2.ipynb',
                period = 10,  # 10min

                slide_win_size = 200, # so timewise it is 200 x 10min = 33,3 hours
                predicted_win_size = 90, # 90 x 10min = 15 hours
                delta_tolerance = 0.02, # +/- 2%

                train_accuracy = 0.4284,
                #train_f1_score = models.FloatField(null=True)
                validation_accuracy = 0.4606,
                #validation_f1_score = models.FloatField(null=True)

                train_data_description = "ETH ETH ETC OMG XRP XMR LTC XEM DASH",
                features_description = '4 : price, volume, price variance, volume variance'
                )
            logger.info("Done.")
        else:
            logger.info(" NN model already exists")
import logging
import time
from django.core.management.base import BaseCommand
from apps.ai.models.nn_model import AnnModel
#from apps.channel.models.exchange_data import POLONIEX
from settings import POLONIEX

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    '''
    Run this command if you need to add a new NN model
    Keras or TF model must be already uploaded to S3
    '''
    help = 'Add all NN models to the database '

    def handle(self, *args, **options):
        logger.info("Adding a new Neural Network model to a database")

        # check if it exists
        # TODO: need to remove that later... it is an ugly way to initialize DB records
        # TODO: change to dictionary of move to migration

        # initial forst model trained on full price data (not price_resampled)
        if not AnnModel.objects.filter(s3_model_file = 'lstm_model_2_2.h5').exists():
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
            logger.info(" lstm_model_2_2.h5 model already exists")


        ######## short, medium and long models for "price_out_of_range" settings, trained on price_resampled data
        if not AnnModel.objects.filter(s3_model_file = 'lstm_short_60m_160_8_3class_return_0.03.h5').exists():
            AnnModel.objects.create(
                timestamp=time.time(),
                source = POLONIEX,
                model_name = 'LSTM',
                s3_model_file = 'lstm_short_60m_160_8_3class_return_0.03.h5',
                s3_notebook_file = 'NA',
                period = 60,  # min

                slide_win_size = 160, # so timewise it is 200 x 10min = 33,3 hours
                predicted_win_size = 8, # 90 x 10min = 15 hours
                delta_tolerance = 0.03, # +/- 2%

                train_accuracy = 0,
                #train_f1_score = models.FloatField(null=True)
                validation_accuracy = 0,
                #validation_f1_score = models.FloatField(null=True)

                train_data_description = "ETH XRP ETC DASH LTC ETH ETC OMG XRP XMR LTC BCH EOS XLM ADA TRX NEO XEM ZEC BNB VET",
                features_description = '4 : price, volume, price variance, volume variance, F1: [0.645 0.232 0.325] ||  PRECISION: [0.884 0.161 0.238]  ||  RECALL: [0.507 0.41  0.513]'
                )
            logger.info("Done.")
        else:
            logger.info(" lstm_short_60m_160_8_3class_return_0.03.h5 model already exists")


        if not AnnModel.objects.filter(s3_model_file = 'lstm_medium_240m_100_20_3class_return_0.1.h5').exists():
            AnnModel.objects.create(
                timestamp=time.time(),
                source = POLONIEX,
                model_name = 'LSTM',
                s3_model_file = 'lstm_medium_240m_100_12_3class_return_0.08.h5',
                s3_notebook_file = 'NA',
                period = 240,  # min

                slide_win_size = 100, # so timewise it is 200 x 10min = 33,3 hours
                predicted_win_size = 12, # 90 x 10min = 15 hours
                delta_tolerance = 0.08, # +/- 2%

                train_accuracy = 0,
                #train_f1_score = models.FloatField(null=True)
                validation_accuracy = 0,
                #validation_f1_score = models.FloatField(null=True)

                train_data_description = "ETH XRP ETC DASH LTC ETH ETC OMG XRP XMR LTC BCH EOS XLM ADA TRX NEO XEM ZEC BNB VET",
                features_description = ' F1: [0.573 0.218 0.257] ||  PRECISION: [0.816 0.135 0.211]  ||  RECALL: [0.441 0.569 0.329]'
                )
            logger.info("Done.")
        else:
            logger.info(" lstm_medium_240m_100_20_3class_return_0.1.h5 model already exists")


        if not AnnModel.objects.filter(s3_model_file = 'lstm_long_1440m_28_10_class3_return_0.1.h5').exists():
            AnnModel.objects.create(
                timestamp=time.time(),
                source = POLONIEX,
                model_name = 'LSTM',
                s3_model_file = 'lstm_long_1440m_28_10_class3_return_0.1.h5',
                s3_notebook_file = 'NA',
                period = 1440,  # min

                slide_win_size = 28, # so timewise it is 200 x 10min = 33,3 hours
                predicted_win_size = 10, # 90 x 10min = 15 hours
                delta_tolerance = 0.1, # +/- 2%

                train_accuracy = 0,
                #train_f1_score = models.FloatField(null=True)
                validation_accuracy = 0,
                #validation_f1_score = models.FloatField(null=True)

                train_data_description = "ETH XRP ETC DASH LTC ETH ETC OMG XRP XMR LTC BCH EOS XLM ADA TRX NEO XEM ZEC BNB VET",
                features_description = ' '
                )
            logger.info("Done.")
        else:
            logger.info(" lstm_long_1440m_28_10_class3_return_0.1.h5 model already exists")


        ##### short, medium  models for "price_max_hit" settings, trained on price_resampled data
        model_name = 'lstm_medium_240m_120_8_maxhit2cl_0.05.h5'
        if not AnnModel.objects.filter(s3_model_file = model_name).exists():
            AnnModel.objects.create(
                timestamp=time.time(),
                source = POLONIEX,
                model_name = 'LSTM',
                s3_model_file = model_name,
                s3_notebook_file = 'NA',
                period = 240,  # min

                slide_win_size = 100, # so timewise it is 200 x 10min = 33,3 hours
                predicted_win_size = 8, # 90 x 10min = 15 hours
                delta_tolerance = 0.05, # +/- 2%

                train_accuracy = 0,
                #train_f1_score = models.FloatField(null=True)
                validation_accuracy = 0,
                #validation_f1_score = models.FloatField(null=True)

                train_data_description = "ETH XRP ETC DASH LTC ETH ETC OMG XRP XMR LTC BCH EOS XLM ADA TRX NEO XEM ZEC BNB VET",
                features_description = ' '
                )
            logger.info("Done.")
        else:
            logger.info("Model " + str(model_name) + " already exists")
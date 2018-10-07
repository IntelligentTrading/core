import time
from settings import SHORT, MEDIUM, LONG, RUN_ANN
from apps.ai.models.nn_model import AnnModel, get_ann_model_object

import logging
logger = logging.getLogger(__name__)


#MODEL_LIST = ["PRICE_PREDICT", "PRICE_MAXHIT"] # , "PRICE_MINHIT"


MODEL_REF = {
    ("PRICE_PREDICT", SHORT)  : 'lstm_short_60m_160_8_3class_return_0.03.h5',
    ("PRICE_PREDICT", MEDIUM) : 'lstm_medium_240m_100_12_3class_return_0.08.h5',
    ("PRICE_PREDICT", LONG)   : 'lstm_model_2_2.h5',

    ("PRICE_MAXHIT", MEDIUM)  : "lstm_medium_240m_120_8_maxhit2cl_0.05.h5"
}


MODELS_PRELOADED = {}
start = time.time()

logger.info("  >> Start loading AI models... ")
for model_name in MODEL_REF:
    ann_model_object = get_ann_model_object(MODEL_REF[model_name])
    MODELS_PRELOADED[model_name] = ann_model_object

logger.info("        ==== Finish loading AI models in time: " + str(time.time()-start) + " ====== ")


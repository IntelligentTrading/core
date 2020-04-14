## Create your tasks here
from __future__ import absolute_import, unicode_literals
import logging

from taskapp.celery import app as celery_app



logger = logging.getLogger(__name__)

## Periodic tasks

############ Indicators
@celery_app.task(retry=False)
def compute_indicators_for_all_sources(resample_period):
    from taskapp.helpers.common import get_tickers
    #logger.info(f"Tickers: {get_tickers(source='all')}")
    for (source, transaction_currency, counter_currency) in get_tickers(source='all'):
        compute_indicators_for.delay(source, transaction_currency, counter_currency, resample_period)

@celery_app.task(retry=False)
def compute_indicators_for(source, transaction_currency, counter_currency, resample_period):
    logger.info("###### Start _compute_indicators_for job #######")
    from taskapp.helpers.indicators import _compute_indicators_for
    _compute_indicators_for(source, transaction_currency, counter_currency, resample_period)



############## ANN
@celery_app.task(retry=False)
def compute_ann_for_all_sources(resample_period):
    logger.info("@@@@@@")
    from taskapp.helpers.common import get_exchanges
    for exchange in get_exchanges():
        compute_ann.delay(source=exchange, resample_period=resample_period)

@celery_app.task(retry=False)
def compute_ann(source, resample_period):
    logger.info("@@@@@@ Start compute_ann indicators job @@@@@@")
    from taskapp.helpers.indicators import _compute_ann
    _compute_ann(source=source, resample_period=resample_period)



# ############# Backtesting
@celery_app.task(retry=False)
def backtest_all_strategies():
    from taskapp.helpers.backtesting import _backtest_all_strategies
    _backtest_all_strategies()


#### Sentiment
@celery_app.task(retry=False)
def compute_sentiment():
    from taskapp.helpers.sentiment_analysis import _analyze_sentiment
    _analyze_sentiment()


# Obsolete
# @celery_app.task(retry=False)
# def compute_and_save_indicators_for_all_sources(resample_period):
#     from taskapp.helpers import get_exchanges
#     for exchange in get_exchanges():
#         compute_and_save_indicators.delay(source=exchange, resample_period=resample_period)


# @celery_app.task(retry=False)
# def compute_and_save_indicators(source, resample_period):
#     from taskapp.helpers.indicators import _compute_and_save_indicators
#     _compute_and_save_indicators(source=source, resample_period=resample_period)


# @shared_task
# def precache_info_bot():
#     from apps.info_bot.helpers import precache_currency_info_for_info_bot
#     precache_currency_info_for_info_bot()


## Debug Tasks
# @shared_task
# def calculate_one_pair(resample_period=SHORT, transaction_currency='BTC', counter_currency = 2):
#     from taskapp.helpers import _calculate_one_par
#     import time
#     timestamp=time.time()
#     logger = logging.getLogger(__name__)
#     _calculate_one_par(timestamp=timestamp, resample_period=resample_period, \
#         transaction_currency=transaction_currency, counter_currency = counter_currency)

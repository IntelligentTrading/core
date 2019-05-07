## Create your tasks here
from __future__ import absolute_import, unicode_literals
import logging

from taskapp.celery import app as celery_app


logger = logging.getLogger(__name__)

# Periodic tasks

# Indicators
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

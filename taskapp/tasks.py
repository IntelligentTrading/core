## Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from settings import SHORT, EXCHANGE_MARKETS

from taskapp.celery import app as celery_app



## Periodic tasks
@celery_app.task(retry=False)
def compute_and_save_indicators_for_all_sources(resample_period):
    from taskapp.helpers import get_exchanges
    for exchange in get_exchanges():
        compute_and_save_indicators.delay(source=exchange, resample_period=resample_period)


@celery_app.task(retry=False)
def compute_and_save_indicators(source, resample_period):
    from taskapp.helpers import _compute_and_save_indicators
    _compute_and_save_indicators(source=source, resample_period=resample_period)


@shared_task
def precache_info_bot():
    from apps.info_bot.helpers import precache_currency_info_for_info_bot
    precache_currency_info_for_info_bot()


## Debug Tasks
# @shared_task
# def calculate_one_pair(resample_period=SHORT, transaction_currency='BTC', counter_currency = 2):
#     from taskapp.helpers import _calculate_one_par
#     import time
#     timestamp=time.time()
#     logger = logging.getLogger(__name__)
#     _calculate_one_par(timestamp=timestamp, resample_period=resample_period, \
#         transaction_currency=transaction_currency, counter_currency = counter_currency)

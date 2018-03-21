## Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from settings import SHORT



## Periodic tasks
@shared_task
def pull_poloniex_data():
    from taskapp.helpers import _pull_poloniex_data
    _pull_poloniex_data()

@shared_task
def compute_and_save_indicators(resample_period_par):
    from taskapp.helpers import _compute_and_save_indicators
    _compute_and_save_indicators(resample_period_par)

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

# @shared_task
# def hello(x):
#     print("Hello, "+x)
# @shared_task
# def hello_world():
#     print("Hello, workd")

# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from apps.channel import helpers



@shared_task
def pull_poloniex_data():
    helpers._pull_poloniex_data()

@shared_task
def compute_and_save_indicators(resample_period_par):
    helpers._compute_and_save_indicators(resample_period_par)

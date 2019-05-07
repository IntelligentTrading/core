from __future__ import absolute_import, unicode_literals
import os
import logging

from celery import Celery
from celery.schedules import crontab

from settings import SHORT, MEDIUM, LONG, RUN_ANN, RUN_SENTIMENT, RUN_BACKTESTING

logger = logging.getLogger(__name__)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    worker_prefetch_multiplier=1, # Disable prefetching
    task_acks_late=True, # Task will be acknowledged after the task has been executed, not just before (the default behavior)
    task_publish_retry=False, # Do not retry tasks in the case of connection loss
    broker_pool_limit=1,
)

# Load task modules from all registered Django app configs.
# Celery auto-discover modules in tasks.py files
app.autodiscover_tasks()

## CELERY Periodic Tasks/Scheduler
##   http://docs.celeryproject.org/en/v4.1.0/userguide/periodic-tasks.html
##   http://docs.celeryproject.org/en/v4.1.0/reference/celery.schedules.html#celery.schedules.crontab
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_):
    from taskapp import tasks

    #calculate SHORT period at the start of the hour
    sender.add_periodic_task(
        crontab(minute=0),  # crontab(minute=3, hour='*')
        tasks.compute_indicators_for_all_sources.s(resample_period=SHORT),
        name='at the beginning of every hour',
        )

    # calculate MEDIUM period at the start of every 4 hours
    sender.add_periodic_task(
        crontab(minute=0, hour='*/4'),
        tasks.compute_indicators_for_all_sources.s(resample_period=MEDIUM),
        name='at the beginning of every 4 hours',
        )

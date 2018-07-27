from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab

from settings import SHORT, MEDIUM, LONG



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

    # Pull poloniex data every minute
    #EVERY_MINUTE = 60
    #sender.add_periodic_task(EVERY_MINUTE, tasks.pull_poloniex_data.s(), name='every %is' % EVERY_MINUTE)

    # Process data and send signals


    # FIRST - calculate ANN for SHORT period at every hour and half OO:30, 01:30 ...
    # @Alex: I put it back to 00:00 because the time stamp is a key and should match hours
    # move it back if server performance sufferrs, but make sure to pass a right timestamp
    sender.add_periodic_task(
        crontab(minute=30),                        #crontab(minute=30, hour='*'),
        tasks.compute_ann_for_all_sources.s(resample_period=SHORT),
        name='at the beginning of every hour', #name='at the beginning of every hour and half',
        )


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

    # calculate LONG period daily at midnight.
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        tasks.compute_indicators_for_all_sources.s(resample_period=LONG),
        name='daily at midnight',
        )



    # LAST - run backtesting daily
    sender.add_periodic_task(
        crontab(minute=40, hour=13),
        tasks.backtest_all_strategies.s(),
        name='daily at 13:40',
        )

    # Precache info_bot every 4 hours
    # from settings import INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS
    #sender.add_periodic_task(INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS, tasks.precache_info_bot.s(), name='every %is' % INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS)


## Non periodic tasks
## Runs tasks, that should start, when worker is ready. Like precaching.
# from celery.signals import worker_ready
# @worker_ready.connect
# def at_start(sender, **kwarg):
#     with sender.app.connection() as conn:
#         sender.app.send_task('taskapp.tasks.precache_info_bot', args=None, connection=conn)

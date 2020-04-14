# ITF Celery tasks queue

Our Celery installation use RabbitMQ broker transport [CloudAMQP heroku add-on](https://elements.heroku.com/addons/cloudamqp).

* [Celery](http://www.celeryproject.org/)
* [Heroku Celery guide](https://devcenter.heroku.com/articles/celery-heroku)

## Celery workers
Heroku can run up to 8 workers in parallel in one dyno, but we run 4 (--concurrency=4), because of memory limitaions.
We use 2 dynos with workers. If more needed - just increase number of heroku dynos. Celery will recognize new dyno and distribute tasks automatically.

## Celery scheduler
We use [RedBeat](https://github.com/sibson/redbeat) as a Celery Beat Scheduler. It  stores data in Redis. [Heroku Redis](https://elements.heroku.com/addons/heroku-redis)

Standard Celery Beat Scheduler saves state in the file and not works great with heroku.

## Requirements

* [Celery](http://docs.celeryproject.org/en/v4.1.0/django/index.html)
* [RedBeat](https://github.com/sibson/redbeat)

## Environment variables

* CELERY_BROKER_URL - url of our redis server (Heroku Redis)

## Files
Celery installed in taskapp/ folder.

* taskapp/celery.py - entry point to Celery
* taskapp/tasks.py - thin wrappers for tasks
* taskapp/helpers/* - tasks

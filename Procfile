release: python manage.py migrate
web: waitress-serve --port=$PORT settings.wsgi:application
worker: REMAP_SIGTERM=SIGQUIT celery --app=taskapp worker --concurrency=4 --hostname=$DYNO@%h -Ofair --purge --without-heartbeat --without-gossip --loglevel=debug
#worker: REMAP_SIGTERM=SIGQUIT celery --app=taskapp worker --concurrency=4 --hostname=$DYNO@%h -Ofair --purge --without-heartbeat --without-gossip --loglevel=info
scheduler: celery --app=taskapp beat --max-interval=10 -S redbeat.RedBeatScheduler
pollqueue: python manage.py poll_queue
infobot: python manage.py run_info_bot
redis_TA_worker: python manage.py TA_worker
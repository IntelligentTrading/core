release: python manage.py migrate
web: waitress-serve --port=$PORT settings.wsgi:application
worker: python manage.py trawl_poloniex
infobot: python manage.py run_info_bot
celery: celery worker --app=celeryapp --loglevel=info # --beat (for scheduler)
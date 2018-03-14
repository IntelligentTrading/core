release: python manage.py migrate
web: waitress-serve --port=$PORT settings.wsgi:application
infobot: python manage.py run_info_bot
celery: celery worker --beat --purge --app=taskapp --loglevel=info
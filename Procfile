release: python manage.py migrate
web: run-program waitress-serve --port=$PORT settings.wsgi:application
worker: python manage.py trawl_poloniex
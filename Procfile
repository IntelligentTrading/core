release: python manage.py migrate
web: newrelic-admin run-program waitress-serve --port=$PORT settings.wsgi:application
worker: python manage.py trawl_poloniex
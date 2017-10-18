release: python manage.py migrate
web: gunicorn settings.wsgi
worker: python manage.py trawl_poloniex
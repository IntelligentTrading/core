# ITF RESTful API

ITF RESTful API allow access to ITF Core Models using HTTP protocol.
You can check documentation at /api/ url or by accessing each API endpoint with browser.

For development and testing start API webserver with command:
`python manage.py runserver`

Add `web: waitress-serve --port=$PORT settings.wsgi:application` to Procfile if you use heroku.

For accessing API on Stage or Production environment set API-KEY parameter in request header.
For LOCAL testing environment API-KEY parameter not needed (set REST_API_SECRET_KEY='' in local_settings.py)

## Requirements

ITF RESTful API uses [Django REST framework](https://github.com/encode/django-rest-framework/tree/master)

### Environment variables and settings

* REST_API_SECRET_KEY - to access API you should set request API-KEY parameter equal to this variable
* CACHE_MIDDLEWARE_SECONDS - cache API responses for this amount of seconds 


## Files
* api/views/ - all API views located in this folder
* api/helpers.py - common code helpers
* api/paginations.py - API uses [CursorPagination](http://www.django-rest-framework.org/api-guide/pagination/#cursorpagination), because it was faster on larger datasets
* api/serializers.py - Serializers

## Endpoints
Defined in api/urls.py

### New API for ITF models
* /v2/history-prices/
* /v2/resampled-prices/
* /v2/signals/
* /v2/prices/
* /v2/volumes/
* /v2/rsi/
* /v2/sma/
* /v2/events-elementary/
* /v2/events-logical/
* /v2/ann-price-classification/

### Tickers API
* /v2/tickers/transaction-currencies/
* /v2/tickers/exchanges/
* /v2/tickers/counter-currencies/
* /v2/itt/

### Old API for ITF models
* /v1/price
* /v1/volumes

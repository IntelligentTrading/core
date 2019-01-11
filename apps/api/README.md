# ITF RESTful API

ITF RESTful API allow access to ITF Core Models using HTTP protocol.
You can check documentation at /api/ url or by accessing each API endpoint with browser.

For development and testing start API webserver with command:
`python manage.py runserver`

Add `web: waitress-serve --port=$PORT settings.wsgi:application` to Procfile if you use heroku.


ITF RESTful API uses simple [token-based HTTP Authentication scheme](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

For clients to authenticate, the token key should be included in the Authorization HTTP header.
The key should be prefixed by the string literal "Token", with whitespace separating the two strings.
For example:
`Authorization: Token 725ea582f6f214bdc8d21437ebd8a13f9717cc56`

To create token use Custom Django Management Command:
`python manage.py generate_api_token username user_telegram_id`

## Requirements

ITF RESTful API uses [Django REST framework](https://github.com/encode/django-rest-framework/tree/master)

### Environment variables and settings

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

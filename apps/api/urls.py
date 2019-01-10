from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from apps.api.views import ann_price_classification, events_elementary, events_logical, \
    history_price, resampled_price, rsi, signal, sma, volume, sentiment
from apps.api.views import tickers, itt



app_name = 'api'

schema_view = get_swagger_view(title='ITT Core API')

urlpatterns = [

    url(r'^v2/signals/coins-with-most-signals/$', signal.CoinsWithMostSignals.as_view(), name='coins-with-most-signals'),
    url(r'^v2/signals/$', signal.ListSignals.as_view(), name='signals'), 

    url(r'^v2/resampled-prices/$', resampled_price.ListPrices.as_view(), name='resampled-prices'),

    url(r'^v2/volumes/$', volume.ListVolumes.as_view(), name='volumes'),

    url(r'^v2/rsi/$', rsi.ListRsis.as_view(), name='rsis'),

    url(r'^v2/events-elementary/$', events_elementary.ListEventsElementary.as_view(), name='events-elementary'),

    # Tickers
    #url(r'^v2/tickers/$', tickers.TickersView.as_view(), name='tickers info'),
    url(r'^v2/tickers/transaction-currencies/$', tickers.TransactionCurrenciesView.as_view(), name='transaction-currencies'),
    url(r'^v2/tickers/exchanges/$', tickers.ExchangesView.as_view(), name='exchanges'),
    url(r'^v2/tickers/counter-currencies/$', tickers.CounterCurrenciesView.as_view(), name='counter-currencies'),

    url(r'^v2/itt/$', itt.ITTPriceView.as_view(), name='itt-price'),

    url(r'^v2/history-prices/$', history_price.ListHistoryPrices.as_view(), name='history-prices'),

    url(r'^v2/events-logical/$', events_logical.ListEventsLogical.as_view(), name='events-logical'),

    url(r'^v2/ann-price-classification/$', ann_price_classification.ListAnnPriceClassification.as_view(), name='ann-price-classification'),

    url(r'^v2/sentiment/$', sentiment.SentimentClassification.as_view(), name='sentiment'),

     url(r'^v2/sma/$', sma.ListSma.as_view(), name='sma'),

    url(r'^$', schema_view), # swagger
 ]

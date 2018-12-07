from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from apps.api.views import ann_price_classification, events_elementary, events_logical, \
    history_price, resampled_price, rsi, signal, sma, volume, price, sentiment
from apps.api.views import tickers, itt
from apps.api.views import v1_price, v1_volume, v1_user, v1_csv

app_name = 'api'

schema_view = get_swagger_view(title='ITT Core API')

urlpatterns = [

    url(r'^user$', v1_user.User.as_view(), name='v1_user'),
    url(r'^users$', v1_user.Users.as_view(), name='v1_users'),

    url(r'^price$', v1_price.Price.as_view(), name='v1_price'),
    url(r'^volume$', v1_volume.Volume.as_view(), name='v1_volume'),

    url(r'^csv$', v1_csv.CSV.as_view(), name='v1_csv'),

    url(r'^v1/user$', v1_user.User.as_view(), name='v1_user'),
    url(r'^v1/users$', v1_user.Users.as_view(), name='v1_users'),

    url(r'^v1/price$', v1_price.Price.as_view(), name='v1_price'),
    url(r'^v1/volume$', v1_volume.Volume.as_view(), name='v1_volume'),

    url(r'^v1/csv$', v1_csv.CSV.as_view(), name='v1_csv'),

#   url(r'^sma$', views.sma.SMA.as_view(), name='sma'),

    url(r'^v2/signals/coins-with-most-signals/$', signal.CoinsWithMostSignals.as_view(), name='coins-with-most-signals'),
    url(r'^v2/signals/$', signal.ListSignals.as_view(), name='signals'), 
    #url(r'^v2/signals/(?P<transaction_currency>.+)$', signal.ListSignal.as_view(), name='signal'),

    url(r'^v2/resampled-prices/$', resampled_price.ListPrices.as_view(), name='resampled-prices'),
    url(r'^v2/resampled-prices/(?P<transaction_currency>.+)$', resampled_price.ListPrice.as_view(), name='resampled-price'),

    url(r'^v2/prices/$', price.ListPrices.as_view(), name='prices'),
    url(r'^v2/prices/(?P<transaction_currency>.+)$', price.ListPrice.as_view(), name='price'),

    url(r'^v2/volumes/$', volume.ListVolumes.as_view(), name='volumes'),
    #url(r'^v2/volumes/(?P<transaction_currency>.+)$', volume.ListVolume.as_view(), name='volume'),

    url(r'^v2/rsi/$', rsi.ListRsis.as_view(), name='rsis'),
    #url(r'^v2/rsi/(?P<transaction_currency>.+)$', rsi.ListRsi.as_view(), name='rsi'),

    url(r'^v2/events-elementary/$', events_elementary.ListEventsElementary.as_view(), name='events-elementary'),
    #url(r'^v2/events-elementary/(?P<transaction_currency>.+)$',  events_elementary.ListEventElementary.as_view(), name='event-elementary'),

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

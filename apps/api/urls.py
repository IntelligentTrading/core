from django.conf.urls import url, include
#from apps.api.views import price, volume, user, csv, signal
from apps.api.views import price, volume, signal, rsi

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Core API')

urlpatterns = [

    # url(r'^user$', user.User.as_view(), name='user'),
    # url(r'^users$', user.Users.as_view(), name='users'),

    #url(r'^price$', price.Price.as_view(), name='price'),
    #url(r'^volume$', volume.Volume.as_view(), name='volume'),
    # url(r'^sma$', views.sma.SMA.as_view(), name='sma'),

    # url(r'^csv$', csv.CSV.as_view(), name='csv'),

    url(r'^signals/$', signal.SignalsListAPIView.as_view(), name='signals'), 
    url(r'^signals/(?P<signal>.+)$',  signal.SignalListAPIView.as_view(), name='signal'),

    url(r'^prices/$',  price.PricesListAPIView.as_view(), name='prices'),
    url(r'^prices/(?P<transaction_currency>.+)$',  price.PriceListAPIView.as_view(), name='price'),

    url(r'^volumes/$',  volume.VolumesListAPIView.as_view(), name='volumes'),
    url(r'^volumes/(?P<transaction_currency>.+)$',  volume.VolumeListAPIView.as_view(), name='volume'),

    url(r'^rsi/$',  rsi.RsisListAPIView.as_view(), name='rsis'),
    url(r'^rsi/(?P<transaction_currency>.+)$',  rsi.RsiListAPIView.as_view(), name='rsi'),
    
    url(r'^$', schema_view), # swagger

]

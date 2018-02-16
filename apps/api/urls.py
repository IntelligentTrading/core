from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view

from apps.api.views import v1_price, v1_volume, v1_user, v1_csv
from apps.api.views import price, volume, signal, rsi


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

    url(r'^v2/signals/$', signal.SignalsListAPIView.as_view(), name='signals'), 
    url(r'^v2/signals/(?P<signal>.+)$',  signal.SignalListAPIView.as_view(), name='signal'),

    url(r'^v2/prices/$',  price.PricesListAPIView.as_view(), name='prices'),
    url(r'^v2/prices/(?P<transaction_currency>.+)$',  price.PriceListAPIView.as_view(), name='price'),

    url(r'^v2/volumes/$',  volume.VolumesListAPIView.as_view(), name='volumes'),
    url(r'^v2/volumes/(?P<transaction_currency>.+)$',  volume.VolumeListAPIView.as_view(), name='volume'),

    url(r'^v2/rsi/$',  rsi.RsisListAPIView.as_view(), name='rsis'),
    url(r'^v2/rsi/(?P<transaction_currency>.+)$',  rsi.RsiListAPIView.as_view(), name='rsi'),
    
    url(r'^$', schema_view), # swagger
 ]

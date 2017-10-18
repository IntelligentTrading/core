from django.conf.urls import url, include
from apps.api.views import price, volume


urlpatterns = [


    url(r'^price$', price.Price.as_view(), name='price'),
    url(r'^volume/$', volume.Volume.as_view(), name='volume'),
    # url(r'^sma/$', views.sma.SMA.as_view(), name='sma'),

]

from django.conf.urls import url, include
from apps.api.views import price, volume, user


urlpatterns = [

    url(r'^user$', user.User.as_view(), name='user'),

    url(r'^price$', price.Price.as_view(), name='price'),
    url(r'^volume$', volume.Volume.as_view(), name='volume'),
    # url(r'^sma$', views.sma.SMA.as_view(), name='sma'),

]

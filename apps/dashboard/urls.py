from django.conf.urls import url, include

from apps.dashboard.views.main import Main
from apps.dashboard.views.market import Market
from apps.dashboard.views.ticker import Ticker

urlpatterns = [

    url(r'^$', Main.as_view(), name='main'),
    url(r'^market$', Market.as_view(), name='main'),
    url(r'^ticker/(?P<ticker_symbol>[-\w\.]+)$', Ticker.as_view(), name='main'),

]

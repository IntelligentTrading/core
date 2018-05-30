from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from apps.dashboard.views.main import Main
# from apps.dashboard.views.market import Market
# from apps.dashboard.views.ticker import Ticker

urlpatterns = [

    url(r'^$', cache_page(3600 * 4)(Main.as_view()), name='main'),

    # url(r'^market$', cache_page(3600 * 12)(Market.as_view()), name='main'),

    # url(r'^ticker/(?P<ticker_symbol>[-\w\.]+)$', cache_page(3600 * 1)(Ticker.as_view()), name='main'),

]

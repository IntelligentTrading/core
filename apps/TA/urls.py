from apps.TA.resources import historical_data, price_volume
from django.conf.urls import url


urlpatterns = [

    url(r'^historical_data/(?P<ticker>[A-Z,1-9]{2,5}_[A-Z]{3,4})$',
        historical_data.HistoricalDataAPI.as_view(), name='historical_data'),

    url(r'^ticker/(?P<ticker>[A-Z,1-9]{2,5}_[A-Z]{3,4})$',
        price_volume.PriceVolumeAPI.as_view(), name='price_volume'),

    # url(r'^ticker/(?P<ticker>[A-Z]{2,5}_[A-Z]{3,4})/SMA$',
    #     sma.SMA.as_view(), name='sma'),

]

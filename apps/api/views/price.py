import json

from django.http import HttpResponse
from django.views.generic import View

from apps.indicator.models import Price as PriceModel


class Price(View):
    def dispatch(self, request, *args, **kwargs):
        return super(Price, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        coin = request.GET.get('coin', "BTC").upper()
        assert len(coin) < 8

        price_object = PriceModel.objects.filter(coin=coin).order_by('-timestamp').first()
        if price_object:
            response = {
                'source': price_object.get_source_display(),
                'coin': price_object.coin,
                'price_satoshis': price_object.satoshis,
                'price_usdt': price_object.usdt,
                'price_satoshis_change': price_object.price_satoshis_change,
                'timestamp': str(price_object.timestamp),
            }
        else:
            response = {
                'error': "Coin not found"
            }

        return HttpResponse(json.dumps(response), content_type="application/json")

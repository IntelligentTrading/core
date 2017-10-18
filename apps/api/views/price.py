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

        price_data = PriceModel.objects.filter(coin=coin).order_by('-timestamp').first()
        if price_data:
            response = {
                'price': price_data.satoshis if coin is not "BTC" else price_data.usdt,
                'timestamp': str(price_data.timestamp)
            }
        else:
            response = {
                'error': "Coin not found"
            }

        return HttpResponse(json.dumps(response), content_type="application/json")


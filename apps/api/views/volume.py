import json

from django.http import HttpResponse
from django.views.generic import View

from apps.indicator.models import Volume as VolumeModel


class Volume(View):
    def dispatch(self, request, *args, **kwargs):
        return super(Volume, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        coin = request.GET.get('coin', "BTC").upper()
        assert len(coin) < 8

        volume_data = VolumeModel.objects.filter(coin=coin).order_by('-timestamp').first()
        if volume_data:
            response = {
                'volume': volume_data.btc_volume if coin is not "BTC" else volume_data.usdt,
                'timestamp': str(volume_data.timestamp)
            }
        else:
            response = {
                'error': "Coin not found"
            }

        return HttpResponse(json.dumps(response), content_type="application/json")

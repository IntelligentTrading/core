import json

from django.http import HttpResponse
from django.views.generic import View

from apps.indicator.models import Volume as VolumeModel


class Volume(View):
    def dispatch(self, request, *args, **kwargs):
        return super(Volume, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        transaction_currency = request.GET.get('transaction_currency', 'NA').upper()

        if transaction_currency == 'NA':
            return HttpResponse(json.dumps({'error': 'transaction_currency parameter is required'}),
                                content_type="application/json")

        assert len(transaction_currency) > 1
        assert len(transaction_currency) < 8

        volume_data = VolumeModel.objects.filter(transaction_currency=transaction_currency
                                                 ).order_by('-timestamp').first()
        if volume_data:
            response = {
                'volume': volume_data.volume if transaction_currency is not "BTC" else volume_data.usdt,
                'timestamp': str(volume_data.timestamp)
            }
        else:
            response = {
                'error': "Coin not found"
            }

        return HttpResponse(json.dumps(response), content_type="application/json")

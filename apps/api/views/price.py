import json

from django.http import HttpResponse
from django.views.generic import View

from apps.indicator.models import Price as PriceModel


class Price(View):
    def dispatch(self, request, *args, **kwargs):
        return super(Price, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        transaction_currency = request.GET.get('transaction_currency', 'NA').upper()
        if transaction_currency == 'NA':
            return HttpResponse(json.dumps({'error': 'transaction_currency parameter is required'}),
                                content_type="application/json")

        assert len(transaction_currency) > 1
        assert len(transaction_currency) < 8

        price_object = PriceModel.objects.filter(transaction_currency=transaction_currency
                                                 ).order_by('-timestamp').first()
        if price_object:
            response = {
                'source': price_object.get_source_display(),
                'transaction_currency': price_object.transaction_currency,
                'counter_currency': price_object.counter_currency,
                'price': price_object.price,
                'price_change': price_object.price_change,
                'timestamp': str(price_object.timestamp),
            }
        else:
            response = {
                'error': "Coin not found"
            }

        return HttpResponse(json.dumps(response), content_type="application/json")

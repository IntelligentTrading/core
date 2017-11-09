import json
import csv
from apps.indicator.models import Price
from django.http import HttpResponse
from django.views.generic import View

class CSV(View):
    def dispatch(self, request, *args, **kwargs):
        return super(CSV, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

        writer = csv.writer(response)
        for price in Price.objects.filter(coin="BTC").all():
            writer.writerow([price.coin, price.price_satoshis, str(price.timestamp)])

        return response

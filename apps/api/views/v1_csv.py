import json
import csv
from apps.indicator.models import Price
from django.http import HttpResponse
from django.views.generic import View

from apps.signal.models import Signal
from apps.user.models.user import LONG_HORIZON


class CSV(View):
    def dispatch(self, request, *args, **kwargs):
        return super(CSV, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        writer = csv.writer(response)

        if request.GET.get('eth_signals', None):

            writer.writerow(["counter_currency", "transaction_currency",
                             "trend",
                             "strength", "max_strength",
                             "signal_sent_at", "signal_created_at"])

            eth_signals = Signal.objects.filter(transaction_currency="ETH")
            eth_signals = eth_signals.filter(horizon=LONG_HORIZON)
            for signal in eth_signals.all():
                writer.writerow([signal.get_counter_currency_display(), signal.transaction_currency,
                                 signal.trend,
                                 signal.strength_value, signal.strength_max,
                                 str(signal.sent_at), str(signal.created_at)])



        elif request.GET.get('btc_prices', None):

            for price in Price.objects.filter(transaction_currency="BTC").all():
                writer.writerow([price.transaction_currency, price.price, str(price.timestamp)])

        return response

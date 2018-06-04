from django.shortcuts import render
from django.views.generic import View

from apps.signal.models import Signal
from settings import COUNTER_CURRENCY_CHOICES, USDT


class Ticker(View):
    def dispatch(self, request, ticker_symbol, *args, **kwargs):
        return super(Ticker, self).dispatch(request, ticker_symbol, *args, **kwargs)

    def get(self, request, ticker_symbol):

        if ticker_symbol.find("_") < 0:
            transaction_currency = ticker_symbol
        else:
            [transaction_currency, counter_currency] = ticker_symbol.split("_")

        counter_currency_int = USDT

        for cc in COUNTER_CURRENCY_CHOICES:
            if cc[1] == counter_currency:
                counter_currency_int = cc[0]


        signals = Signal.objects.filter(transaction_currency=transaction_currency,
                                        counter_currency=counter_currency_int
                                        ).order_by("-sent_at")[:5]

        context = {
            "ticker_symbol": ticker_symbol,
            "tv_ticker_symbol": ticker_symbol.replace("_", ""),
            "signals": signals,
        }
        return render(request, 'ticker.html', context)

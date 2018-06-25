from django.shortcuts import render
from django.views.generic import View

from apps.indicator.models import Price, Volume
from apps.signal.models import Signal
from settings import COUNTER_CURRENCY_CHOICES, USDT, BINANCE


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

        price = Price.objects.filter(transaction_currency=transaction_currency,
                                    counter_currency=counter_currency_int,
                                    source=BINANCE
                                    ).order_by('-timestamp').first()

        volume = Volume.objects.filter(transaction_currency=transaction_currency,
                                    counter_currency=counter_currency_int,
                                    source=BINANCE
                                    ).order_by('-timestamp').first()

        signals = Signal.objects.filter(transaction_currency=transaction_currency,
                                        counter_currency=counter_currency_int
                                        ).order_by("-sent_at")[:10]

        context = {
            "ticker_symbol": ticker_symbol,
            "transaction_currency": transaction_currency,
            "counter_currency": counter_currency,
            "price": price,
            "price_display": '{:.2f}'.format(price.price) if price.counter_currency == USDT else '{:.4g}'.format(price.price),
            "volume_display": '{:.2f}'.format(volume.volume) if price.counter_currency == USDT else '{:.4g}'.format(volume.volume),
            "volume": volume,
            "tv_ticker_symbol": ticker_symbol.replace("_", ""),
            "signals": signals,
        }
        return render(request, 'ticker.html', context)

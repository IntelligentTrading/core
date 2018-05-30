from django.shortcuts import render
from django.views.generic import View


class Ticker(View):
  def dispatch(self, request, ticker_symbol, *args, **kwargs):
    return super(Ticker, self).dispatch(request, ticker_symbol, *args, **kwargs)

  def get(self, request, ticker_symbol):
    context = {}
    return render(request, 'ticker.html', context)

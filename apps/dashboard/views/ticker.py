from django.shortcuts import render, redirect
from django.views.generic import View


class Ticker(View):
  def dispatch(self, request, ticker_symbol, *args, **kwargs):
    return super(Ticker, self).dispatch(request, *args, **kwargs)

  def get(self, request):
    context = {}
    return render(request, 'ticker.html', context)

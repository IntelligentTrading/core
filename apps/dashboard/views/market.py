from django.shortcuts import render
from django.views.generic import View


class Market(View):
  def dispatch(self, request, *args, **kwargs):
    return super(Market, self).dispatch(request, *args, **kwargs)

  def get(self, request):
    context = {}
    return render(request, 'market.html', context)

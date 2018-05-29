from django.shortcuts import render, redirect
from django.views.generic import View


class Main(View):
  def dispatch(self, request, *args, **kwargs):
    return super(Main, self).dispatch(request, *args, **kwargs)

  def get(self, request):
    context = {}
    return render(request, 'main.html', context)

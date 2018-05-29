from django.conf.urls import url, include

from apps.dashboard.views.main import Main

urlpatterns = [

    url(r'^$', Main.as_view(), name='main'),

]

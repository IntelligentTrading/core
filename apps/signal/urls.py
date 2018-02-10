from django.conf.urls import url

from apps.signal.api import views

urlpatterns = [
    # /signal/api/
    url(
        regex=r'^api/$',
        view=views.SignalListAPIView.as_view(),
        name='signal_rest_api'
    ),
]
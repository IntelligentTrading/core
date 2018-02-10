from django.conf.urls import url

from apps.signal.api import views

urlpatterns = [
    # /signal/api/
    url(
        regex=r'^api_v1/$',
        view=views.SignalListAPIView.as_view(),
        name='signal_rest_api'
    ),
]
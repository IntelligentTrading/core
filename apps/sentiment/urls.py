from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from apps.sentiment.views import sentiment_dashboard

app_name = 'sentiment'

schema_view = get_swagger_view(title='ITT Core API')

urlpatterns = [
    url(r'^$', sentiment_dashboard.sentiment_index, name='sentiment'),
]

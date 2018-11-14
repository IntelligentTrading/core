from django.conf.urls import url
from apps.sentiment.views.sentiment_dashboard import SentimentDashboard

app_name = 'sentiment'

urlpatterns = [
    url(r'^$', SentimentDashboard.as_view(), name='sentiment'),
]

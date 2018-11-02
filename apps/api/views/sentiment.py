from rest_framework.generics import ListAPIView

from apps.api.serializers import SentimentSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp
from settings import REDDIT, VADER


from django.shortcuts import render
from apps.indicator.models.sentiment import Sentiment



class SentimentClassification(ListAPIView):

    permission_classes = (RestAPIPermission,)
    pagination_class = StandardResultsSetPagination
    serializer_class = SentimentSerializer
    filter_fields = ('sentiment_source', 'topic', 'model', 'timestamp')

    model = serializer_class.Meta.model

    def get_queryset(self):
        return filter_queryset_by_timestamp(self)


def sentiment_index(request):
    latest_data = Sentiment.objects.filter(sentiment_source=REDDIT, model=VADER, topic='BTC').order_by('-timestamp')[:1]
    context = {'btc_reddit': latest_data[0]}
    return render(request, 'sentiment_index.html', context)
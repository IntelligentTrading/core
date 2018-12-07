from rest_framework.generics import ListAPIView

from apps.api.serializers import SentimentSerializer
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp



class SentimentClassification(ListAPIView):

    pagination_class = StandardResultsSetPagination
    serializer_class = SentimentSerializer
    filter_fields = ('sentiment_source', 'topic', 'model', 'timestamp')

    model = serializer_class.Meta.model

    def get_queryset(self):
        return filter_queryset_by_timestamp(self)


from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.api.serializers import SentimentSerializer
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp



class SentimentClassification(ListAPIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    serializer_class = SentimentSerializer
    filter_fields = ('sentiment_source', 'topic', 'model', 'timestamp')

    model = serializer_class.Meta.model

    def get_queryset(self):
        return filter_queryset_by_timestamp(self)


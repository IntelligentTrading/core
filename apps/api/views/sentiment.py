from rest_framework.generics import ListAPIView

from apps.api.serializers import SentimentSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp  # , queryset_for_list_with_resample_period



class SentimentClassification(ListAPIView):

    permission_classes = (RestAPIPermission,)
    pagination_class = StandardResultsSetPagination
    serializer_class = SentimentSerializer
    filter_fields = ('sentiment_source', 'topic', 'model', 'timestamp')

    model = serializer_class.Meta.model

    def get_queryset(self):
        return self.model.objects
        queryset = filter_queryset_by_timestamp(self)



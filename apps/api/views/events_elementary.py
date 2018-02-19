from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import EventsElementarySerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.indicator.models import EventsElementary


class EventsElementaryListAPIView(ListAPIView):
    queryset = EventsElementary.objects.order_by('-timestamp')
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = EventsElementarySerializer

class EventElementaryListAPIView(ListAPIView):
    permission_classes = (RestAPIPermission, )
    serializer_class = EventsElementarySerializer
    pagination_class = OneRecordPagination

    model = serializer_class.Meta.model
    def get_queryset(self):
        event_name = self.kwargs['event_name']
        queryset = self.model.objects.filter(event_name=event_name)
        return queryset.order_by('-timestamp')

from rest_framework.generics import ListAPIView

from apps.api.serializers import SignalSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.signal.models import Signal

class SignalsListAPIView(ListAPIView):
    queryset = Signal.objects.order_by('-timestamp') # last signal will be on top/first
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = SignalSerializer

class SignalListAPIView(ListAPIView):
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
    pagination_class = StandardResultsSetPagination

    model = serializer_class.Meta.model
    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        return queryset.order_by('-timestamp')

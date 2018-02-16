from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import RsiSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.indicator.models import Rsi


class RsisListAPIView(ListAPIView):
    queryset = Rsi.objects.order_by('-timestamp')
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = RsiSerializer

class RsiListAPIView(ListAPIView):
    permission_classes = (RestAPIPermission, )
    serializer_class = RsiSerializer
    pagination_class = OneRecordPagination

    model = serializer_class.Meta.model
    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        return queryset.order_by('-timestamp')

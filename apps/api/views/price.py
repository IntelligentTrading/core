from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import PriceSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination

from apps.indicator.models import Price


class PricesListAPIView(ListAPIView):
    queryset = Price.objects.order_by('-timestamp')
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = PriceSerializer

class PriceListAPIView(ListAPIView):
    permission_classes = (RestAPIPermission, )
    serializer_class = PriceSerializer
    pagination_class = StandardResultsSetPagination

    model = serializer_class.Meta.model
    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        return queryset.order_by('-timestamp')

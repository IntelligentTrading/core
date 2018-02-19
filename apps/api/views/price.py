from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import PriceSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from settings import PERIODS_LIST

from apps.indicator.models import PriceResampl


class PricesListAPIView(ListAPIView):
    short_period = PERIODS_LIST[0] # 1min in secs
    queryset = PriceResampl.objects.exclude(midpoint_price__isnull=True # filter empty records
    ).filter(resample_period=short_period).order_by('-timestamp')
    
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = PriceSerializer

class PriceListAPIView(ListAPIView):
    permission_classes = (RestAPIPermission, )
    serializer_class = PriceSerializer
    pagination_class = OneRecordPagination

    model = serializer_class.Meta.model
    def get_queryset(self):
        short_period = PERIODS_LIST[0]
        transaction_currency = self.kwargs['transaction_currency']
        # midpoint_price must not be empty, short resample perion 1min
        queryset = self.model.objects.exclude(midpoint_price__isnull=True
        ).filter(transaction_currency=transaction_currency, resample_period=short_period)

        return queryset.order_by('-timestamp')

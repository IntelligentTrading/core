from rest_framework.generics import ListAPIView

from apps.api.serializers import PriceSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from settings import PERIODS_LIST

from apps.indicator.models import PriceResampl, Price

#from django_filters.rest_framework import DjangoFilterBackend

SHORT_PERIOD = PERIODS_LIST[0] # PERIODS_LIST = [60, 240, 1440] in minutes

class PricesListAPIView(ListAPIView):
    """
    Show List of Prices from PriceResampl model for short resampl period - 60min.
    """ 
    queryset = PriceResampl.objects.exclude(midpoint_price__isnull=True # filter empty records
    ).filter(resample_period=SHORT_PERIOD).order_by('-timestamp')
    
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = PriceSerializer

    filter_fields = ('source', 'transaction_currency', 'counter_currency')

class PriceListAPIView(ListAPIView):
    """
    Show last price from PriceResampl model for short resampl period - 60min.
    
    Default counter_currency is BTC. For BTC itself, counter_currency is USDT.
    """
    
    permission_classes = (RestAPIPermission, )
    serializer_class = PriceSerializer
    pagination_class = OneRecordPagination

    model = serializer_class.Meta.model

    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        if transaction_currency == 'BTC':
            counter_currency = Price.USDT
        else:
            counter_currency = Price.BTC
        # midpoint_price must not be empty
        queryset = self.model.objects.exclude(midpoint_price__isnull=True
        ).filter(transaction_currency=transaction_currency, counter_currency=counter_currency, \
                    resample_period=SHORT_PERIOD)

        return queryset.order_by('-timestamp')

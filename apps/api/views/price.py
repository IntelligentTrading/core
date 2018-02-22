from rest_framework.generics import ListAPIView

from apps.api.serializers import PriceSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import default_counter_currency, filter_queryset_by_timestamp

from settings import PERIODS_LIST

from apps.indicator.models import PriceResampl



SHORT_PERIOD = PERIODS_LIST[0] # PERIODS_LIST = [60, 240, 1440] in minutes

class ListPrices(ListAPIView):
    """Return a list of all the prices from PriceResampl model for short resampl period - 60min.
    Exclude prices with empty midpoint_price

    /api/v2/prices/

    URL query parameters:

    For filtering:

        transaction_currency: -- string 'BTC', 'ETH' etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:

        page_size -- number of results to return per page (Default: 100)
        page -- page number within the paginated result set

    Examples:
        /api/v2/prices/?startdate=2018-01-26T10:24:37&enddate=2018-01-26T10:59:02
        /api/v2/prices/?transaction_currency=ETH&counter_currency=0
        /api/v2/prices/?page_size=1&page=3
    """
     
    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = PriceSerializer

    filter_fields = ('source', 'transaction_currency', 'counter_currency')

    model = serializer_class.Meta.model
    
    def get_queryset(self):
        queryset = self.model.objects.exclude(midpoint_price__isnull=True \
        ).filter(resample_period=SHORT_PERIOD).order_by('-timestamp')
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset


class ListPrice(ListAPIView):
    """Return a list of prices from PriceResampl model for {transaction_currency} with default counter_currency. 
    Short resample period 60 min, non empty midpoint_price. 
    Default counter_currency is BTC. For BTC itself, counter_currency is USDT.
    
    /api/v2/prices/{transaction_currency}

    URL query parameters:

    For filtering:

        counter_currency -- number: 0=BTC, 1=ETH, 2=USDT, 3=XMR (Default 0, for BTC - 2)
        source -- number: 0=poloniex, 1=bittrex
        startdate -- show inclusive from date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination:

        page_size -- number of results to return per page (Default 1)
        page -- page number within the paginated result set

    Examples:
        /api/v2/prices/ETH # ETH in BTC
        /api/v2/prices/ETH?counter_currency=2 # ETH in USDT
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = PriceSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        counter_currency = default_counter_currency(transaction_currency)
        # midpoint_price must not be empty
        queryset = self.model.objects.exclude(midpoint_price__isnull=True
        ).filter(transaction_currency=transaction_currency, counter_currency=counter_currency, \
                    resample_period=SHORT_PERIOD).order_by('-timestamp')
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset

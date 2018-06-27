from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import SmaSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp



# Model: SMA
class ListSma(ListAPIView):
    """Return list of SMA.

    /api/v2/sma/

    URL query parameters

    For filtering

        sma_period -- number 20, 30, 50, 120, 200 ... 
        transaction_currency -- string BTC, ETH etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, SHORT = 60
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Example
        /api/v2/sma/?source=1&resample_period=60&transaction_currency=XMR&sma_period=200&startdate=2018-06-27T10:03:00

    """

    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = SmaSerializer

    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency', 'sma_period')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset


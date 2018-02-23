from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import RsiSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp

from apps.indicator.models import Rsi



class ListRsis(ListAPIView):
    """Return a list of RSI.

    /api/v2/rsi/

    URL query parameters:

    For filtering:

        transaction_currency -- string BTC, ETH etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:

        page_size -- number of results to return per page (Default 100)
        page -- page number within the paginated result set

    Examples:
        /api/v2/rsi/?transaction_currency=BTC
        /api/v2/rsi/?startdate=2018-02-10T22:14:37&enddate=2018-01-26T11:08:30
    """

    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = RsiSerializer

    filter_fields = ('transaction_currency', 'counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = self.model.objects.order_by('-timestamp')
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset


class ListRsi(ListAPIView):
    """Return a list of RSI for {transaction_currency}.
    
    /api/v2/rsi/{transaction_currency}

    URL query parameters:

    For filtering:

        counter_currency -- number: 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination:

        page_size -- number of results to return per page (Default 1)
        page -- page number within the paginated result set

    Examples:
        /api/v2/rsi/BTC
        /api/v2/rsi/BTC?counter_currency=2&startdate=2018-01-26T11:08:30
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = RsiSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset.order_by('-timestamp')

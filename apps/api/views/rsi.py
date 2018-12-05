from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_with_resample_period
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination
from apps.api.serializers import RsiSerializer


# Mode: RSI
class ListRsis(ListAPIView):
    """Return list of RSI.

    /api/v2/rsi/

    URL query parameters

    For filtering

        transaction_currency -- string BTC, ETH etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, SHORT = 60
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Examples

        /api/v2/rsi/?transaction_currency=BTC
        /api/v2/rsi/?startdate=2018-02-10T22:14:37&enddate=2018-01-26T11:08:30
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    serializer_class = RsiSerializer

    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset


class ListRsi(ListAPIView):
    """Return list of RSI for {transaction_currency}.
    
    /api/v2/rsi/{transaction_currency}

    URL query parameters

    For filtering

        counter_currency -- number: 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT
        source -- number 0=poloniex, 1=bittrex, 2=binance.
        resample_period -- in minutes. Default SHORT = 60
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Examples

        /api/v2/rsi/BTC
        /api/v2/rsi/BTC?counter_currency=2&startdate=2018-01-26T11:08:30
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RsiSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('source', 'counter_currency')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_with_resample_period(self)
        return queryset

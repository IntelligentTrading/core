from rest_framework.generics import ListAPIView

from apps.api.serializers import SignalSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_with_resample_period

from apps.signal.models import Signal



class ListSignals(ListAPIView):
    """Return list of signals.

    /api/v2/signals/

    URL query parameters

    For filtering

        transaction_currency -- string BTC, ETH etc
        transaction_currencies -- string with symbols divided by +, like: ETH+XRP+OMG
        signal -- string SMA, RSI
        trend -- 1, -1
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, SHORT = 60
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)
        horizon -- 0=SHORT, 1=MEDIUM , 2=LONG
        id -- id in database, like 186208


    For pagination

        cursor -- indicator that the client may use to page through the result set
        page_size -- a numeric value indicating the page size

    Examples

        /api/v2/signals/?transaction_currency=ETH&signal=RSI
        /api/v2/signals/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
    pagination_class = StandardResultsSetPagination

    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency', 'signal', 'trend', 'horizon', 'id')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        transaction_currencies = self.request.query_params.get('transaction_currencies', None)
        if transaction_currencies:
            transaction_currencies_list = [x.strip() for x in transaction_currencies.split(' ')]
            queryset = queryset.filter(transaction_currency__in=transaction_currencies_list)
        return queryset


class ListSignal(ListAPIView):
    """Return list of signals for {transaction_currency}.
    
    /api/v2/signals/{transaction_currency}

    URL query parameters

    For filtering

        signal -- string SMA, RSI
        trend -- 1, -1
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT
        source -- number 0=poloniex, 1=bittrex, 2=binance.
        resample_period -- in minutes. Default SHORT = 60
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format
        horizon -- 0=SHORT, 1=MEDIUM , 2=LONG


    For pagination

        cursor - indicator that the client may use to page through the result set
        page_size -- a numeric value indicating the page size

    Examples

        /api/v2/signals/ETH
        /api/v2/signals/ETH?signal=RSI
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('source', 'counter_currency', 'signal', 'trend')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_with_resample_period(self)
        return queryset

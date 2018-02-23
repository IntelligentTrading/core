from rest_framework.generics import ListAPIView

from apps.api.serializers import SignalSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp

from apps.signal.models import Signal



class ListSignals(ListAPIView):
    """Return a list of all signals.

    /api/v2/signals/

    URL query parameters

    For filtering

        transaction_currency -- string BTC, ETH etc
        signal -- string SMA, RSI
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination

        page_size -- number of results to return per page (Default 100)
        page -- page number within the paginated result set

    Examples
        /api/v2/signals/?transaction_currency=ETH&signal=RSI
        /api/v2/signals/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
    pagination_class = StandardResultsSetPagination

    filter_fields = ('signal', 'transaction_currency', 'counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = self.model.objects.order_by('-timestamp')
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset


class ListSignal(ListAPIView):
    """Return a list of signals for {transaction_currency}.
    
    /api/v2/signals/{transaction_currency}

    URL query parameters

    For filtering

        signal -- string SMA, RSI
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination

        page_size -- number of results to return per page (Default 1)
        page -- page number within the paginated result set

    Examples
        /api/v2/signals/ETH
        /api/v2/signals/ETH?signal=RSI
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = SignalSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('signal', 'counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset.order_by('-timestamp')

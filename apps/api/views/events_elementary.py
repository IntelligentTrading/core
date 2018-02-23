from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import EventsElementarySerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp

from apps.indicator.models import EventsElementary



class ListEventsElementary(ListAPIView):
    """Return a list of elementary events.

    /api/v2/events-elementary/

    URL query parameters:

    For filtering:

        transaction_currency -- string BTC, ETH etc
        event_name -- string sma200_cross_price_up, lagging_above_highest
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:

        page_size -- number of results to return per page (Default 100)
        page -- page number within the paginated result set

    Examples:
        /api/v2/events-elementary/?transaction_currency=ETH&event_name=sma200_cross_price_down
        /api/v2/events-elementary/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
    """

    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = EventsElementarySerializer
    filter_fields = ('event_name', 'transaction_currency', 'counter_currency', 'source')

    model = serializer_class.Meta.model
    def get_queryset(self):
        queryset = self.model.objects.order_by('-timestamp')
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset

class ListEventElementary(ListAPIView):
    """Return a list of elementary events for {transaction_currency}.

    /api/v2/events-elementary/{transaction_currency}

    URL query parameters

    For filtering

        event_name -- string sma200_cross_price_up, lagging_above_highest
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination

        page_size -- number of results to return per page (Default 1)
        page -- page number within the paginated result set

    Examples
        /api/v2/events-elementary/BTC
        /api/v2/events-elementary/BTC?event_name=conversion_below_base
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = EventsElementarySerializer
    pagination_class =  OneRecordPagination

    filter_fields = ('event_name', 'counter_currency', 'source')

    model = serializer_class.Meta.model
    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        queryset = self.model.objects.filter(transaction_currency=transaction_currency)
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset.order_by('-timestamp')

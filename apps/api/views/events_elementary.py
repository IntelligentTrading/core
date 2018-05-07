from rest_framework.generics import ListAPIView

from rest_framework.views import APIView

from apps.api.serializers import EventsElementarySerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_with_resample_period

from apps.indicator.models import EventsElementary



class ListEventsElementary(ListAPIView):
    """Return list of elementary events.

    /api/v2/events-elementary/

    URL query parameters:

    For filtering:

        transaction_currency -- string BTC, ETH etc
        event_name -- string sma200_cross_price_up, lagging_above_highest
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, SHORT = 60
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:
        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Examples:
        /api/v2/events-elementary/?transaction_currency=ETH&event_name=sma200_cross_price_down
        /api/v2/events-elementary/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
    """

    permission_classes = (RestAPIPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = EventsElementarySerializer
    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency', 'event_name')

    model = serializer_class.Meta.model
    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset

class ListEventElementary(ListAPIView):
    """Return list of elementary events for {transaction_currency}.

    /api/v2/events-elementary/{transaction_currency}

    URL query parameters

    For filtering

        event_name -- string sma200_cross_price_up, lagging_above_highest
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT
        source -- number 0=poloniex, 1=bittrex, 2=binance.
        resample_period -- in minutes. Default SHORT = 60
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination
        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Examples
        /api/v2/events-elementary/BTC
        /api/v2/events-elementary/BTC?event_name=conversion_below_base
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = EventsElementarySerializer
    pagination_class =  OneRecordPagination

    filter_fields = ('source', 'counter_currency', 'event_name')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_with_resample_period(self)
        return queryset 

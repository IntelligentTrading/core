from rest_framework.generics import ListAPIView

from apps.api.helpers import filter_queryset_by_timestamp
from apps.api.paginations import StandardResultsSetPagination
from apps.api.serializers import EventsElementarySerializer


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

    pagination_class = StandardResultsSetPagination
    serializer_class = EventsElementarySerializer
    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency', 'event_name')

    model = serializer_class.Meta.model
    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset

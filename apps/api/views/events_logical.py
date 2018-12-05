from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.api.serializers import EventsLogicalSerializer
from apps.api.paginations import StandardResultsSetPagination

from apps.api.helpers import filter_queryset_by_timestamp  # , queryset_for_list_with_resample_period


#  model: EventsLogical
class ListEventsLogical(ListAPIView):
    """Return list of logcal events.

    /api/v2/events-logical/

    URL query parameters:

    For filtering:

        event_name -- string kumo_breakout_down_signal, kumo_breakout_up_signal, RSI_Cumulative_bullish, RSI_Cumulative, RSI_Cumulative_bearish
        transaction_currency -- string BTC, ETH etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, 60=short period
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination:

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Example:

        /api/v2/events-logical/?event_name=kumo_breakout_up_signal&source=0&transaction_currency=ZEC&resample_period=60&startdate=2018-06-14T01:00:00
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    serializer_class = EventsLogicalSerializer
    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency', 'event_name')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset

from rest_framework import exceptions
from rest_framework.generics import ListAPIView

from apps.api.serializers import HistoryPriceSerializer
from apps.api.paginations import StandardResultsSetPaginationOnlyTimestamp

from apps.api.helpers import filter_queryset_by_timestamp_history


# Model: PriceHistory
class ListHistoryPrices(ListAPIView):
    """Return list of prices from HistoryPrice model. Please use startdate and enddate.
    When startdate is not set, API return records for the last month.

    /api/v2/history-prices/

    URL query parameters

    For filtering

        transaction_currency: -- string 'BTC', 'ETH' etc (required)
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR (required)
        source -- number 0=poloniex, 1=bittrex, 2=binance (required)
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination

        cursor - indicator that the client may use to page through the result set
        page_size -- a numeric value indicating the page size

    Examples

        /api/v2/history-prices/?source=0&transaction_currency=ETH&counter_currency=0&startdate=2018-01-26T10:24:37&enddate=2018-01-26T10:59:02
    """

    pagination_class = StandardResultsSetPaginationOnlyTimestamp
    serializer_class = HistoryPriceSerializer

    filter_fields = ('source', 'transaction_currency', 'counter_currency')

    model = serializer_class.Meta.model

    def get_queryset(self):
        # check required parameters
        for param in ('source', 'transaction_currency', 'counter_currency'):
            if param not in self.request.query_params:
                raise exceptions.NotFound(detail=f"Missing required parameter: {param}")

        queryset = filter_queryset_by_timestamp_history(self)
        return queryset
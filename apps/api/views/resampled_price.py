from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_with_resample_period
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination
from apps.api.serializers import ResampledPriceSerializer


class ListPrices(ListAPIView):
    """Return list of resampled prices from PriceResampl model for all resample periods.

    /api/v2/resampled-prices/

    URL query parameters

    For filtering

        transaction_currency: -- string 'BTC', 'ETH' etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        resample_period -- in minutes, SHORT=60
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Results

        price_change_24h - calculated (current close_price - 24h old close_price)/current close_price

    Examples

        /api/v2/resampled-prices/?startdate=2018-01-26T10:24:37&enddate=2018-01-26T10:59:02
        /api/v2/resampled-prices/?transaction_currency=ETH&counter_currency=0&resample_period=60
    """
     
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    serializer_class = ResampledPriceSerializer

    filter_fields = ('source', 'resample_period', 'transaction_currency', 'counter_currency')

    model = serializer_class.Meta.model
    
    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset


class ListPrice(ListAPIView):
    """Return list of resampled prices from PriceResampl model for {transaction_currency} with default counter_currency. 
    Short resample period 60 min by default. 
    Default counter_currency is BTC. For BTC itself, counter_currency is USDT.
    
    /api/v2/resampled-prices/{transaction_currency}

    URL query parameters

    For filtering

        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT.
        source -- number 0=poloniex, 1=bittrex, 2=binance.
        resample_period -- in minutes. Default SHORT = 60
        startdate -- show inclusive from date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination

        cursor - the pagination cursor value
        page_size -- a numeric value indicating the page size

    Results

        price_change_24h - calculated (current close_price - 24h old close_price)/current close_price

    Examples

        /api/v2/resampled-prices/ETH # ETH in BTC
        /api/v2/resampled-prices/ETH?counter_currency=2 # ETH in USDT
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ResampledPriceSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('source', 'counter_currency')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_with_resample_period(self)
        return queryset

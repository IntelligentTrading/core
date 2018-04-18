from rest_framework.generics import ListAPIView

from apps.api.serializers import VolumeSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_without_resample_period

from apps.indicator.models import Volume



class ListVolumes(ListAPIView):
    """Return list of price volumes.

    /api/v2/volumes/

    URL query parameters

    For filtering

        transaction_currency -- string 'BTC', 'ETH' etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex, 2=binance
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    For pagination
        cursor - indicator that the client may use to page through the result set

    Examples
        /api/v2/volumes/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
        /api/v2/volumes/?transaction_currency=ETH&counter_currency=0
        /api/v2/volumes/?page_size=1&page=3
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = VolumeSerializer
    pagination_class = StandardResultsSetPagination

    filter_fields = ('transaction_currency', 'counter_currency', 'source')

    model = serializer_class.Meta.model
    
    def get_queryset(self):
        queryset = filter_queryset_by_timestamp(self)
        return queryset


class ListVolume(ListAPIView):
    """Return list of price volumes for {transaction_currency} with default counter_currency.
    
    /api/v2/volumes/{transaction_currency}

    URL query parameters

    For filtering

        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT
        source -- number 0=poloniex, 1=bittrex, 2=binance. Default 0=poloniex
        startdate -- show inclusive from this date. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    For pagination
        cursor - indicator that the client may use to page through the result set

    Examples
        /api/v2/volumes/ETH # ETH in BTC
        /api/v2/volumes/ETH?counter_currency=2 # ETH in USDT
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = VolumeSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_without_resample_period(self)
        return queryset

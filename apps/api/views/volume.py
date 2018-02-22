from dateutil.parser import parse

from rest_framework.generics import ListAPIView

from apps.api.serializers import VolumeSerializer
from apps.api.permissions import RestAPIPermission
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

from apps.api.helpers import default_counter_currency

from apps.indicator.models import Volume


class ListVolumes(ListAPIView):
    """Return a list of all the existing price volumes.

    /api/v2/volumes/

    URL query parameters:

    for filtering:

        transaction_currency: -- string 'BTC', 'ETH' etc
        counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
        source -- number 0=poloniex, 1=bittrex
        startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
        enddate -- to this date (inclusive)

    for pagination:

        page_size -- number of results to return per page (Default: 100)
        page -- page number within the paginated result set

    Examples:
        /api/v2/volumes/?startdate=2018-02-10T22:14:37&enddate=2018-02-10T22:27:58
        /api/v2/volumes/?transaction_currency=ETC&counter_currency=0
        /api/v2/volumes/?page_size=1&page=3
    """

    permission_classes = (RestAPIPermission, )
    serializer_class = VolumeSerializer
    pagination_class = StandardResultsSetPagination

    filter_fields = ('transaction_currency', 'counter_currency', 'source')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = self.model.objects.order_by('-timestamp')
        startdate = self.request.query_params.get('startdate', None)
        enddate = self.request.query_params.get('enddate', None)
        if startdate is not None:
            startdate = parse(startdate) # DRF has problem with 2018-02-12T09:09:15
            #startdate = datetime.datetime.strptime(startdate, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            queryset = queryset.filter(timestamp__gte=startdate)
        if enddate is not None:
            enddate = parse(enddate)
            queryset = queryset.filter(timestamp__lte=enddate)
        return queryset


class ListVolume(ListAPIView):
    """Return a list of price volumes for {transaction_currency} with default counter_currency.
    
    /api/v2/volumes/{transaction_currency}

    URL query parameters:

    for filtering:

        counter_currency -- number: 0=BTC, 1=ETH, 2=USDT, 3=XMR (Default 0, for BTC - 2)
        source -- number: 0=poloniex, 1=bittrex
        startdate -- show inclusive from this date formatted %Y-%m-%dT%H:%M:%S'. For example 2018-02-12T09:09:15
        enddate -- until this date inclusive in same format

    for pagination:

        page_size -- number of results to return per page (Default 1)
        page -- page number within the paginated result set

    Examples:
        /api/v2/volumes/ETH # ETH in BTC
        /api/v2/volumes/ETH?&counter_currency=2 # ETH in USDT
    """
    permission_classes = (RestAPIPermission, )
    serializer_class = VolumeSerializer
    pagination_class = OneRecordPagination

    model = serializer_class.Meta.model

    def get_queryset(self):
        transaction_currency = self.kwargs['transaction_currency']
        counter_currency = default_counter_currency(transaction_currency)
        queryset = self.model.objects.filter(transaction_currency=transaction_currency, counter_currency=counter_currency)
        return queryset.order_by('-timestamp')

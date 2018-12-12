from datetime import datetime, timedelta

from apps.signal.models import Signal

from django.db.models import Count, Avg, IntegerField, Sum
from django.db.models.functions import Cast

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_with_resample_period
from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination
from apps.api.serializers import SignalSerializer


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

    serializer_class = SignalSerializer
    pagination_class = OneRecordPagination

    filter_fields = ('source', 'counter_currency', 'signal', 'trend')

    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = queryset_for_list_with_resample_period(self)
        return queryset


class CoinsWithMostSignals(ListAPIView):
    """Return list of coins ordered by number of emitted signals.

    /api/v2/signals/coins-with-most-signals/

    URL query parameters:

        maxresults -- the maximum number of records retrieved. Default 10.
        timeframe -- number of hours past from start. Default 1.
        start -- last, from last signal, now, from now. Default last.

    Examples:

        /api/v2/signals/coins-with-most-signals/?maxresults=20&timeframe=24&start=now
    """

    def get(self, request, format=None):
        maxresults = int(request.query_params.get('maxresults', 10))
        timeframe = int(request.query_params.get('timeframe', 1))
        start = request.query_params.get('start', 'last')
        return Response(get_coins_with_most_signals(maxresults, timeframe, start))


# Helpers methods
def get_coins_with_most_signals(maxresults, timeframe, start):
    if start == 'now':
        from_date = datetime.now()
    else:
        from_date = Signal.objects.values('timestamp')\
            .order_by('-timestamp')[0]['timestamp']
    dtimeframe = from_date - timedelta(hours=int(timeframe))

    return Signal.objects.values('transaction_currency')\
            .annotate(signal_counts=Count('*'))\
            .annotate(average_trend=Avg(Cast('trend', IntegerField())))\
            .order_by('-signal_counts')\
            .filter(timestamp__gte=dtimeframe)[:maxresults]


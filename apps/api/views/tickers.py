from datetime import timedelta, datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.api.permissions import RestAPIPermission

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, EXCHANGE_MARKETS, COUNTER_CURRENCIES

from taskapp.helpers import get_exchanges, get_currency_pairs, get_source_code
from apps.api.helpers import group_items
from apps.indicator.models import Price



class TransactionCurrenciesView(APIView):
    '''Return available transaction_currencies for one source or all sources.\n

    /api/v2/tickers/transaction-currencies\n

    For filtering\n
        exchange -- exchange market name 'poloniex', 'binance',  etc
        transaction_currency: -- string 'BTC', 'ETH' etc

    Examples\n
        /api/v2/tickers/transaction-currencies # for all sources
        /api/v2/tickers/transaction-currencies?exchange=binance # only for Binance
        /api/v2/tickers/transaction-currencies?transaction_currency=LTC # sources and counter_currencies for LTC
    '''

    permission_classes = (RestAPIPermission, )

    def get(self, request, format=None):
        exchange = request.query_params.get('exchange', None)
        transaction_currency = request.query_params.get('transaction_currency', None)

        print(transaction_currency)

        timestamp_qs = Price.objects.values('timestamp').order_by('-timestamp')
        res_qs = Price.objects.values('source', 'transaction_currency', 'counter_currency')

        if (exchange is not None) and (exchange in EXCHANGE_MARKETS):
            source =  get_source_code(exchange)
            timestamp_qs = timestamp_qs.filter(source=source)
            res_qs = res_qs.filter(source=source)

        if transaction_currency is not None:
            timestamp_qs = timestamp_qs.filter(transaction_currency=transaction_currency)
            res_qs = res_qs.filter(transaction_currency=transaction_currency)
        
        to_timestamp = timestamp_qs.first()['timestamp']
        from_timestamp = timestamp_qs.filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).first()['timestamp']
        res = res_qs.filter(timestamp__range=(from_timestamp, to_timestamp)).distinct()
        return Response(group_items(res))
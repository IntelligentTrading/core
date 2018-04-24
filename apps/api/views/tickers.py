from datetime import timedelta, datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.api.permissions import RestAPIPermission

from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES, EXCHANGE_MARKETS, COUNTER_CURRENCIES

from taskapp.helpers import get_exchanges, get_currency_pairs
from apps.api.helpers import group_items
from apps.indicator.models import Price


# class TickersView(APIView):
#     """
#     Return tickers info

#     /api/v2/tickers/"
#     """

#     permission_classes = (RestAPIPermission, )

#     def get(self, request, format=None): 
#         return Response({
#             'exchanges': EXCHANGE_MARKETS,
#             'counter-currencies': COUNTER_CURRENCIES,
#          })


# def get_currency_pairs(source, period_in_seconds):
#     """
#     Return: [('BTC', 0), ('PINK', 0), ('ETH', 0),....]
#     """
#     get_from_time = time.time() - period_in_seconds
#     price_objects = Price.objects.values('transaction_currency', 'counter_currency').filter(source=source).filter(timestamp__gte=get_from_time).distinct()
#     return [(item['transaction_currency'], item['counter_currency']) for item in price_objects]

#def get_currency_pairs_from_exchanges(sources, period_in_seconds)





class TransactionCurrenciesView(APIView):
    '''Return available transaction_currencies for one source or all sources.\n

    /api/v2/tickers/transaction-currencies\n

    For filtering\n
        source -- number 0=poloniex, 1=bittrex, 2=binance
        transaction_currency: -- string 'BTC', 'ETH' etc
        

    Examples\n
        /api/v2/tickers/transaction-currencies # for all sources
        /api/v2/tickers/transaction-currencies?source=2 # only for Binance
        /api/v2/tickers/transaction-currencies?transaction-currency=LTC # sources and counter_currencies for LTC
    '''

    permission_classes = (RestAPIPermission, )

    def get(self, request, format=None):
        source = request.query_params.get('source', None)
        transaction_currency = request.query_params.get('transaction_currency', None)

        timestamp_qs = Price.objects.values('timestamp').order_by('-timestamp')
        #from_timestamp_qs = Price.objects.values('timestamp').order_by('-timestamp')
        res_qs = Price.objects.values('source', 'transaction_currency', 'counter_currency')

        if (source is not None) and (int(source) in get_exchanges()):
            timestamp_qs = timestamp_qs.filter(source=source)
            # from_timestamp_qs = from_timestamp_qs.filter(source=source)
            res_qs = res_qs.filter(source=source)

        if transaction_currency is not None:
            timestamp_qs = timestamp_qs.filter(transaction_currency=transaction_currency)
            # from_timestamp_qs = from_timestamp_qs.filter(transaction_currency=transaction_currency)
            res_qs = res_qs.filter(transaction_currency=transaction_currency)
        
        to_timestamp = timestamp_qs.first()['timestamp']
        from_timestamp = timestamp_qs.filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).first()['timestamp']
        res = res_qs.filter(timestamp__range=(from_timestamp, to_timestamp)).distinct()
        

        # if (source is not None) and (int(source) in get_exchanges()): # filter('source'=source).
        #     to_timestamp = Price.objects.values('timestamp').filter(source=source).order_by('-timestamp').first()['timestamp']
        #     from_timestamp = Price.objects.values('timestamp').filter(source=source).filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).order_by('-timestamp').first()['timestamp']
        #     res = Price.objects.filter(source=source).filter(timestamp__range=(from_timestamp, to_timestamp)).values('source','transaction_currency','counter_currency').distinct()
        # else:
        #     to_timestamp = Price.objects.values('timestamp').order_by('-timestamp').first()['timestamp']
        #     from_timestamp = Price.objects.values('timestamp').filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).order_by('-timestamp').first()['timestamp']
        #     res = Price.objects.filter(timestamp__range=(from_timestamp, to_timestamp)).values('source','transaction_currency','counter_currency').distinct()

        return Response(group_items(res)) #res) #([{symbol:BTC, exchange: Binance},{symbol:BTC, exchange: Poloniex}])


# class CounterCurrenciesView(APIView):
#     """Return available transaction_currencies for one source or all sources.

#     /api/v2/tickers/transaction-currencies

#     For filtering
#         source -- number 0=poloniex, 1=bittrex, 2=binance
#         transaction_currency: -- string 'BTC', 'ETH' etc

#     Examples
#         /api/v2/tickers/transaction-currencies # for all sources
#         /api/v2/tickers/transaction-currencies?source=2 # only for Binance
#         /api/v2/tickers/transaction-currencies?source=2 # only for Binance
#     """

#     permission_classes = (RestAPIPermission, )

#     def get(self, request, format=None):
#         source = request.query_params.get('source', None)

#         if (source is not None) and (int(source) in get_exchanges()): # filter('source'=source).
#             to_timestamp = Price.objects.values('timestamp').filter(source=source).order_by('-timestamp').first()['timestamp']
#             from_timestamp = Price.objects.values('timestamp').filter(source=source).filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).order_by('-timestamp').first()['timestamp']
#             res = Price.objects.filter(source=source).filter(timestamp__range=(from_timestamp, to_timestamp)).values('source','transaction_currency','counter_currency').distinct()
#         else:
#             to_timestamp = Price.objects.values('timestamp').order_by('-timestamp').first()['timestamp']
#             from_timestamp = Price.objects.values('timestamp').filter(timestamp__lte=to_timestamp - timedelta(minutes=60*4)).order_by('-timestamp').first()['timestamp']
#             res = Price.objects.filter(timestamp__range=(from_timestamp, to_timestamp)).values('source','transaction_currency','counter_currency').distinct()

#         return Response(group_items(res))


# class TransactionCurrenciesForSourceView(APIView):
#     """
#     /api/v2/tickers/transaction-currencies"
#     """
    


#     def list(self, request):
#         serializer = serializers.TaskSerializer(
#             instance=tasks.values(), many=True)
#         return Response(serializer.data)



# from rest_framework.response import Response 

# class ServerTimeView(APIView): 
#     def get(self, request, format=None): 
#         return Response({ 
#                 'server_time': datetime.datetime.utcnow() 
#                 }) 

# from rest_framework.generics import ListAPIView

# from apps.api.serializers import PriceSerializer
# from apps.api.permissions import RestAPIPermission
# from apps.api.paginations import StandardResultsSetPagination, OneRecordPagination

# from apps.api.helpers import filter_queryset_by_timestamp, queryset_for_list_without_resample_period

# from apps.indicator.models import Price



# class ListPrices(ListAPIView):
#     """Return list of prices from Price model. Thise are raw, non resampled prices from exchange tickers.

#     /api/v2/prices/

#     URL query parameters

#     For filtering

#         transaction_currency: -- string 'BTC', 'ETH' etc
#         counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR
#         source -- number 0=poloniex, 1=bittrex, 2=binance
#         startdate -- from this date (inclusive). Example 2018-02-12T09:09:15
#         enddate -- to this date (inclusive)

#     For pagination
#         cursor - indicator that the client may use to page through the result set

#     Examples
#         /api/v2/prices/?startdate=2018-01-26T10:24:37&enddate=2018-01-26T10:59:02
#         /api/v2/prices/?transaction_currency=ETH&counter_currency=0
#     """
     
#     permission_classes = (RestAPIPermission, )
#     pagination_class = StandardResultsSetPagination
#     serializer_class = PriceSerializer

#     filter_fields = ('source', 'transaction_currency', 'counter_currency')

#     model = serializer_class.Meta.model
    
#     def get_queryset(self):
#         queryset = filter_queryset_by_timestamp(self, self.model.objects)
#         return queryset


# class ListPrice(ListAPIView):
#     """Return list of prices from Price model for {transaction_currency} with default counter_currency. 
#     Default counter_currency is BTC. For BTC itself, counter_currency is USDT.
    
#     /api/v2/prices/{transaction_currency}

#     URL query parameters

#     For filtering

#         counter_currency -- number 0=BTC, 1=ETH, 2=USDT, 3=XMR. Default 0=BTC, for BTC 2=USDT
#         source -- number 0=poloniex, 1=bittrex, 2=binance. Default 0=poloniex. 
#         startdate -- show inclusive from date. For example 2018-02-12T09:09:15
#         enddate -- until this date inclusive in same format

#     For pagination
#         cursor - indicator that the client may use to page through the result set

#     Examples
#         /api/v2/prices/ETH # ETH in BTC
#         /api/v2/prices/ETH?counter_currency=2 # ETH in USDT
#     """

#     permission_classes = (RestAPIPermission, )
#     serializer_class = PriceSerializer
#     pagination_class = OneRecordPagination

#     filter_fields = ('source', 'counter_currency')

#     model = serializer_class.Meta.model

#     def get_queryset(self):
#         queryset = queryset_for_list_without_resample_period(self)
#         return queryset

"""
Helpers and common methods for our REST API
"""

from dateutil.parser import parse

from apps.indicator.models import Price


def default_counter_currency(transaction_currency):
    if transaction_currency == 'BTC':
            counter_currency = Price.USDT
    else:
            counter_currency = Price.BTC
    return counter_currency


# for api.views
def filter_queryset_by_timestamp(self, queryset):
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

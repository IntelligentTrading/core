"""
Helpers and common methods for RESTful API
"""

from dateutil.parser import parse

from apps.indicator.models import Price

from settings import SHORT, POLONIEX



def default_counter_currency(transaction_currency):
    if transaction_currency == 'BTC':
        counter_currency = Price.USDT
    else:
        counter_currency = Price.BTC
    return counter_currency


# for api.views

def filter_queryset_by_timestamp(self, queryset=None):
        startdate = self.request.query_params.get('startdate', None)
        enddate = self.request.query_params.get('enddate', None)

        if queryset is None:
            queryset = self.model.objects

        if startdate is not None:
            startdate = parse(startdate) # Because DRF has problems with dates formatted like 2018-02-12T09:09:15
            queryset = queryset.filter(timestamp__gte=startdate)
        if enddate is not None:
            enddate = parse(enddate)
            queryset = queryset.filter(timestamp__lte=enddate)
        return queryset

def queryset_for_list_with_resample_period(self):
    source = self.request.query_params.get('source', POLONIEX) # Set source POLNIEX by default
    transaction_currency = self.kwargs['transaction_currency']
    counter_currency = default_counter_currency(transaction_currency)
    resample_period = self.request.query_params.get('resample_period', SHORT) # SHORT resample period by default

    queryset = self.model.objects.filter(
        source = source,
        resample_period = resample_period,
        transaction_currency=transaction_currency,
        counter_currency=counter_currency,
    )
    queryset = filter_queryset_by_timestamp(self, queryset)
    return queryset

def queryset_for_list_without_resample_period(self): # for Price and Volume
        source = self.request.query_params.get('source', POLONIEX) # Set source POLNIEX by default
        transaction_currency = self.kwargs['transaction_currency']
        counter_currency = default_counter_currency(transaction_currency)

        queryset = self.model.objects.filter(
            source=source,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
        )
        queryset = filter_queryset_by_timestamp(self, queryset)
        return queryset
"""
Helpers and common methods for RESTful API
"""
import copy
from dateutil.parser import parse

from taskapp.helpers import get_source_name

from settings import SHORT, USDT, BTC, COUNTER_CURRENCY_CHOICES, SOURCE_CHOICES



def default_counter_currency(transaction_currency):
    if transaction_currency == 'BTC':
        counter_currency = USDT
    else:
        counter_currency = BTC
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
    source = self.request.query_params.get('source', None) # Return from the all sources by default
    transaction_currency = self.kwargs['transaction_currency']
    counter_currency = default_counter_currency(transaction_currency)
    resample_period = self.request.query_params.get('resample_period', SHORT) # SHORT resample period by default

    if source:
        queryset = self.model.objects.filter(
            source = source,
            resample_period = resample_period,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
        )
    else:
        queryset = self.model.objects.filter(
            resample_period = resample_period,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
        )

    queryset = filter_queryset_by_timestamp(self, queryset)
    return queryset

def queryset_for_list_without_resample_period(self): # for Price and Volume
    source = self.request.query_params.get('source', None) # Return from the all sources by default
    transaction_currency = self.kwargs['transaction_currency']
    counter_currency = default_counter_currency(transaction_currency)
    if source:
        queryset = self.model.objects.filter(
            source=source,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
        )
    else:
        queryset = self.model.objects.filter(
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
        )

    queryset = filter_queryset_by_timestamp(self, queryset)
    return queryset

def replace_exchange_code_with_name(items):
    replaced = {}
    for item in items:
        item['exchange'] = get_source_name(item['source'])
        item.pop('source', None)
        replaced.update(item)
    return items

def group_items(items, key='transaction_currency', group_by=None):
    if group_by is None:
        group_by = ['exchange', 'counter_currency'] # default group_by

    grouped = {}
    initial_item = {key: [] for key in group_by}

    for item in items:
        if item[key] not in grouped:
            grouped[item[key]] = copy.deepcopy(initial_item)
            grouped[item[key]][key] = item[key]
        for group in group_by:
            if item[group] not in grouped[item[key]][group]:
                grouped[item[key]][group].append(item[group])
    return list(grouped.values())

def get_counter_currency_index(counter_currency_name):
    "return 2 for counter_currency_name='USDT'"
    return next((index for index, cc_name in COUNTER_CURRENCY_CHOICES if cc_name == counter_currency_name), None)

def get_source_index(source_name):
    "return 2 for source_name=binance"
    return next((index for index, source_text in SOURCE_CHOICES if source_text == source_name), None)

from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import logging

from django.core.management.base import BaseCommand

from apps.indicator.models import PriceHistory, Volume
from apps.indicator.management.helpers import DataFiller



logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fill missing volumes in PriceHistory from Indicator.Volume."

    def add_arguments(self, parser):
        parser.add_argument('iterations', type=int)

    def handle(self, *args, **options):
        fill_all_price_history_missing_volumes(options['iterations'])


def fill_all_price_history_missing_volumes(iterations):
    df = DataFiller(name='fill_price_history_missing_volumes', iterations=iterations, save_state_every=10000)
    df.state_property = 'timestamp'

    if df.state is None:
        to_datetime = datetime.now()
    else:
        to_datetime = parse(df.state)
    from_datetime = to_datetime - relativedelta(months=3) # process last 3 months

    df.filler_function = fill_one_price_history_missing_volume_from_indicator_price

    df.input_queryset = PriceHistory.objects.filter(volume__isnull=True, timestamp__gte=from_datetime, timestamp__lte=to_datetime).order_by('-timestamp')
    df.run()


def fill_one_price_history_missing_volume_from_indicator_price(price_history_object):
    pho = price_history_object
    trading_trio = (source, transaction_currency, counter_currency) = (pho.source, pho.transaction_currency, pho.counter_currency)

    logger.info(f">{trading_trio}>PriceHistory id: {pho.id}")

    volume_from_indicator_price = find_closest_volume_for(pho)
    if volume_from_indicator_price is not None:
        pho.volume = volume_from_indicator_price
        pho.save()
        logger.info(f">{trading_trio}>Saved with Volume {volume_from_indicator_price}")
    else:
        logger.info(f">{trading_trio}>Volume not found in Indicator.Volume")

def find_closest_volume_for(pr):
    timestamp = pr.timestamp
    vols = Volume.objects.filter(source=pr.source, transaction_currency=pr.transaction_currency, counter_currency=pr.counter_currency).filter(timestamp__gte=timestamp-timedelta(seconds=30), timestamp__lte=timestamp+timedelta(seconds=30))
    lowest_time_delta = 99999999
    ret_vol = None
    for vol in vols:
        current_time_delta = abs((timestamp - vol.timestamp).total_seconds())
        if current_time_delta < lowest_time_delta:
            ret_vol = vol.volume
            lowest_time_delta = current_time_delta
    return ret_vol
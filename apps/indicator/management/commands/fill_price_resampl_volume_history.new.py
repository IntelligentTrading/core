"""
This is unfinished/untested refactored version of command. Please don't use it.
"""

from datetime import datetime, timedelta
import numpy as np

import logging

from django.core.management.base import BaseCommand

from apps.indicator.models import PriceResampl, PriceHistory, Volume

from apps.indicator.management.helpers import DataFiller


logger = logging.getLogger(__name__)



def test_filler_function(item):
    print(item.__dict__)

class Command(BaseCommand):
    help = "Fill history of volumes in PriceResampl."

    def add_arguments(self, parser):
        parser.add_argument('iterations', type=int)

    def handle(self, *args, **options):
        fill_pr = DataFiller(name='fill_price_resampl_with_volumes', iterations=options['iterations'],  save_state_every=500)

        last_timestamp = fill_pr.state or datetime.now()

        fill_pr.state_property = 'timestamp'
        fill_pr.filler_function = fill_volumes_for_one_price_resampl
        #fill_pr.filler_function = test_filler_function
        fill_pr.input_queryset = PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False, timestamp__lte=last_timestamp).order_by('-timestamp')

        fill_pr.run()


def fill_volumes_for_one_price_resampl(price_resampl):
    trading_trio = (source, transaction_currency, counter_currency) = (price_resampl.source, price_resampl.transaction_currency, price_resampl.counter_currency)
    resample_period = price_resampl.resample_period
    logger.info(f">{trading_trio} R:{resample_period}>Started PR {price_resampl.id}")

    timepoint = price_resampl.timestamp # datetime.utcfromtimestamp(price_resampl['timestamp'])

    transaction_currency_price_list = list(
        PriceHistory.objects.filter(
            source=source,
            transaction_currency=transaction_currency,
            counter_currency=counter_currency,
            timestamp__lte=timepoint,
            timestamp__gte=timepoint - timedelta(minutes=resample_period)
        ).values('timestamp', 'volume').order_by('-timestamp'))

    if transaction_currency_price_list:
        volumes = np.array([rec['volume'] for rec in transaction_currency_price_list])
        open_volume = float(volumes[0])
        close_volume = float(volumes[-1])
        low_volume = float(volumes.min())
        high_volume = float(volumes.max())

        price_resampl.open_volume=open_volume
        price_resampl.close_volume=close_volume
        price_resampl.low_volume=low_volume
        price_resampl.high_volume=high_volume

        price_resampl.save()

        logger.info(f">{trading_trio} R:{resample_period}>Saved volumes ({close_volume}) to PR: {price_resampl.id}")
    else:
        logger.info(f">{trading_trio} R:{resample_period}>No prices to fill PR:{price_resampl.id}. Skipping.")

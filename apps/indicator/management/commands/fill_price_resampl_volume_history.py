from datetime import datetime, timedelta
import numpy as np

import logging

from django.core.management.base import BaseCommand

from apps.indicator.models import PriceResampl, PriceHistory, Volume

from apps.indicator.management.helpers import save_state_to_s3, read_state_from_s3



logger = logging.getLogger(__name__)

S3_KEY_FOR_STATE = 'fill_price_resampl_volume_history_state'


class Command(BaseCommand):
    help = "Fill history of volumes in PriceResampl."

    def add_arguments(self, parser):
        parser.add_argument('iterations', type=int)

    def handle(self, *args, **options):
        iterations = options['iterations']

        last_timestamp = read_state_from_s3(S3_KEY_FOR_STATE) # last timestamp with error

        count = PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False).count()
        logger.info(f"Starting. There are {count} PR objects to fill")

        fill_volume_for_priceresample_with_empty_volume_backward(iterations, last_timestamp)


def fill_volume_for_priceresample_with_empty_volume_backward(number_of_iterations, last_timestamp=None):
    iterated = False
    errors = 0
    if last_timestamp is None:
        last_timestamp = datetime.now()
    # get price resampl with empty volume starting from last one
    price_resample_objects = PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False, timestamp__lte=last_timestamp).order_by('-timestamp')[:number_of_iterations].iterator()

    for idx, price_resampl in enumerate(price_resample_objects):
        iterated = True
        try:
            fill_volumes_for_one_price_resampl(price_resampl, idx)
        except Exception as e:
            logger.error(f"Error filling prices. {e}")
            errors += 1
            if errors > 100:
                errors = 0
                save_state_to_s3(price_resampl.timestamp, S3_KEY_FOR_STATE)

    if not iterated:
        logger.info(">>> All Done. No more PR with empty jobs to do! <<<")


def fill_volumes_for_one_price_resampl(price_resampl, idx=0):
    trading_trio = (source, transaction_currency, counter_currency) = (price_resampl.source, price_resampl.transaction_currency, price_resampl.counter_currency)
    resample_period = price_resampl.resample_period
    logger.info(f"{idx}>{trading_trio} R:{resample_period}>Started PR {price_resampl.id}")

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

        logger.info(f"{idx}>{trading_trio} R:{resample_period}>Saved volumes ({close_volume}) to PR: {price_resampl.id}")
    else:
        logger.info(f"{idx}>{trading_trio} R:{resample_period}>No prices to fill PR:{price_resampl.id}. Skipping.")


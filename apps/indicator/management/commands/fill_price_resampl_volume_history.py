from datetime import datetime, timedelta
import numpy as np
import time

import logging

from django.core.management.base import BaseCommand

from apps.indicator.models import PriceResampl, PriceHistory

#from settings import PERIODS_LIST, SHORT, MEDIUM, LONG



logger = logging.getLogger(__name__)

#PERIODS_TO_CALCS = 5

class Command(BaseCommand):
    help = "Fill history of volumes in PriceResampl."

    def add_arguments(self, parser):
        parser.add_argument('iterations', type=int)

    def handle(self, *args, **options):
        iterations = options['iterations']
        count = PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False).count()
        logger.info(f"Starting. There are {count} PR objects to fill")

        fill_volume_for_priceresample_with_empty_volume_backward(iterations)
        #resample_period=SHORT
        #fill_priceresampl_volume_hist(resample_period=resample_period, periods_to_calc=PERIODS_TO_CALCS)


def fill_volume_for_priceresample_with_empty_volume_backward(number_of_iterations):
    iterated = False
    # get price resampl with empty volume starting from last one
    for idx, price_resampl in enumerate(PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False).order_by('-timestamp')[:number_of_iterations].iterator()):
        iterated = True
        fill_volumes_for_one_price_resampl(price_resampl, idx)

    if not iterated:
        logger.info(">>> All Done. No more PR with empty jobs to do! <<<")


def fill_volumes_for_one_price_resampl(price_resampl, idx=0):
    start_time = time.time()

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

        logger.info(f"{idx}>{trading_trio} R:{resample_period}>Saved volumes ({close_volume}) to PR: {price_resampl.id}, {int(time.time() - start_time)}s")
    else:
        logger.info(f"{idx}>{trading_trio} R:{resample_period}>No prices to fill PR:{price_resampl.id}. Skipping.")


# def get_trios_source_trading_pair(back_in_time_seconds=4*60*60, blacklisted_coins=None):
#     """
#     Return[(source, transaction_currency, counter_currency), (source1, transaction_currency, counter_currency) ...]
#     Return: [(0, 'BTC', 0), (1, 'BTC', 0), (2, 'BTC', 0),....]

#     set back_in_time_seconds=None to get all trios from beginning
#     """
#     if blacklisted_coins is None:
#         blacklisted_coins = BLACKLISTED_COINS
#     price_objects = PriceHistory.objects.values('source', 'transaction_currency', 'counter_currency')
#     if back_in_time_seconds is not None:
#         get_from_time = time.time() - back_in_time_seconds
#         price_objects = price_objects.filter(timestamp__gte=get_from_time)
#     price_objects = price_objects.distinct()
#     return [(item['source'], item['transaction_currency'], item['counter_currency']) for item in price_objects if item['transaction_currency'] not in blacklisted_coins]

# def fill_priceresampl_volume_hist(resample_period, periods_to_calc):
#     logger.info("Go...")
#     # get trading_trios = [(source, transaction_currency, counter_currency), (source1, transaction_currency, counter_currency) ...]
#     trading_trios = get_trios_source_trading_pair(back_in_time_seconds=None, blacklisted_coins=[]) # all from beginning
#     for trading_trio in trading_trios:
#         fill_priceresampl_volume_for_one_trading_trio(trading_trio, resample_period, periods_to_calc)


# def fill_priceresampl_volume_for_one_trading_trio(trading_trio, resample_period, periods_to_calc):
#     (source, transaction_currency, counter_currency) = trading_trio # (0, 'STEEM', 1)
#     logger.info(f"{trading_trio} Starting calcs for: {periods_to_calc} periods")
#     # we will go backward
    
#     # first without volume
#     first_resampled_price = PriceResampl.objects.values('timestamp').filter(source=source, transaction_currency=transaction_currency, counter_currency=counter_currency, resample_period=resample_period)\
#                                         .filter(close_volume__isnull=True).order_by('timestamp').first()['timestamp']
#     # first with volume
#     first_price_from_history = PriceHistory.objects.values('timestamp').filter(source=source, transaction_currency=transaction_currency, counter_currency=counter_currency)\
#                                         .filter(volume__isnull=False).order_by('timestamp').first()['timestamp']
#     first_price_from_history = first_price_from_history + timedelta(minutes=resample_period)

#     last_timestamp_for_calc = first_resampled_price if first_resampled_price < first_price_from_history else first_price_from_history

#     # going backwards
#     iterated = False
#     for price_resampl in PriceResampl.objects.filter(source=source, transaction_currency=transaction_currency, counter_currency=counter_currency, resample_period=resample_period)\
#         .filter(close_volume__isnull=True, timestamp__gte=last_timestamp_for_calc).order_by('-timestamp')[:periods_to_calc].iterator():
    
#         iterated = True
#         logger.info(f">{trading_trio}>Calculating volumes for PR: {price_resampl.id}")
        
#         timepoint = price_resampl.timestamp # datetime.utcfromtimestamp(price_resampl['timestamp'])
#         transaction_currency_price_list = list(
#             PriceHistory.objects.filter(
#                 source=source,
#                 transaction_currency=transaction_currency,
#                 counter_currency=counter_currency,
#                 timestamp__lte=timepoint,
#                 timestamp__gte=timepoint - timedelta(minutes=resample_period)
#             ).values('timestamp', 'close', 'volume').order_by('-timestamp'))

#         # # skip the currency if there is no given price
#         if transaction_currency_price_list:
#             # prices = np.array([rec['close'] for rec in transaction_currency_price_list])

#             # open_price = int(prices[0])
#             # close_price = int(prices[-1])
#             # low_price = int(prices.min())
#             # high_price = int(prices.max())
#             # midpoint_price = int((high_price + low_price) / 2)
#             # mean_price = int(prices.mean())
#             # price_variance = prices.var()

#             volumes = np.array([rec['volume'] for rec in transaction_currency_price_list])
#             open_volume = float(volumes[0])
#             close_volume = float(volumes[-1])
#             low_volume = float(volumes.min())
#             high_volume = float(volumes.max())

#             price_resampl.open_volume=open_volume
#             price_resampl.close_volume=close_volume
#             price_resampl.low_volume=low_volume
#             price_resampl.high_volume=high_volume
#             #print(price_resampl.__dict__)
#             price_resampl.save()
#             logger.info(f">{trading_trio}>Saved volumes ({close_volume}) to PR: {price_resampl.id}")
#         else:
#             logger.info(f">{trading_trio}>No prices to fill PR:{price_resampl.id}. Skipping...")
#         #import pdb; pdb.set_trace()

#     if not iterated:
#         logger.info(">>> All Done for resampled period {resample_period}. No more jobs to do! <<<")








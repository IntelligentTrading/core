import logging

from apps.api.permissions import RestAPIPermission
from settings.redis_db import database
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.TA.storages.data.pv_history import defualt_price_indexes, default_volume_indexes, PriceVolumeHistoryStorage
from apps.TA.storages.abstract.timeseries_storage import StorageException
from apps.TA.storages.data.price import PriceStorage


# ["open_price", "close_price", "low_price", "high_price",
# "midpoint_price", "mean_price", "price_variance",
# "open_volume", "close_volume", "low_volume", "high_volume",]

logger = logging.getLogger(__name__)


class PriceVolumeAPI(APIView):
    permission_classes = (RestAPIPermission,)

    def get(self, request, ticker):

        ticker = ticker or request.query_params.get('ticker')
        exchange = request.query_params.get('exchange')
        timestamp = request.query_params.get('timestamp')
        index = request.query_params.get('index')

        results_dict = PriceVolumeHistoryStorage.query(
            ticker=ticker,
            exchange=exchange,
            index=index,
            timestamp=timestamp)

        if len(results_dict) and not 'error' in results_dict:
            return Response(results_dict, status=status.HTTP_200_OK)
        else:
            return Response(results_dict, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, ticker):
        """
        This should receive a json dictionary of
        5 min resampled price and/or volume
        for the upcoming or nearly past 5min period
        closing at the provided unix timestamp
        where timestamp is an int divisible by 300s (5 min)
        """

        ticker = ticker or request.data.get('ticker')
        exchange = request.data.get('exchange')
        timestamp = request.data.get('timestamp')

        # SAVE VALUES IN REDIS USING PriceStorage OBJECT
        pipeline = database.pipeline(transaction=False)

        try:
            p = PriceStorage(ticker=ticker,
                             exchange=exchange,
                             timestamp=timestamp)
            # v = VolumeStorage(ticker=args['ticker'],
            #                  exchange=args['exchange'],
            #                  timestamp=args['timestamp'])


        except StorageException as e:
            return {'error': str(e)}, 400  #bad request

        for index in defualt_price_indexes:
            price_index_value = request.data.get(index, None)
            if price_index_value:
                p.index = index
                p.value = price_index_value
                pipeline = p.save(pipeline=pipeline)

        # for index in default_volume_indexes:
        #     volume_index_value = request.data.get(index, None)
        #     if volume_index_value:
        #         v.index = index
        #         v.value = volume_index_value
        #         pipeline = v.save(pipeline=pipeline)

        try:
            database_response = pipeline.execute()
            return Response({
                       'success': f'{sum(database_response)} db entries created'
                   }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                       'error': str(e)
                   }, status=status.HTTP_501_NOT_IMPLEMENTED)

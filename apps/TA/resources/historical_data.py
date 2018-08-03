import logging

from apps.api.permissions import RestAPIPermission
from settings.redis_db import database
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, defualt_price_indexes, default_volume_indexes

logger = logging.getLogger(__name__)


class HistoricalDataAPI(APIView):
    permission_classes = (RestAPIPermission,)

    def put(self, request, ticker):
        """
        This should receive a resampled price
        for the upcoming or nearly past 5min period
        where timestamp is divisible by 300s (5 min)
        and represents a resampled data point for
        :return:
        """


        ticker = ticker or request.data.get('ticker')
        exchange = request.data.get('exchange')
        timestamp = request.data.get('timestamp')

        # SAVE VALUES IN REDIS USING PriceVolumeHistoryStorage OBJECT
        pipeline = database.pipeline() # transaction=False

        # CREATE OBJECT FOR STORAGE
        data_history = PriceVolumeHistoryStorage(
            ticker=ticker,
            exchange=exchange,
            timestamp=timestamp
        )
        data_history_objects = {}


        for index in defualt_price_indexes + default_volume_indexes:
            index_value = request.data.get(index, None)
            if index_value:
                data_history.index = index
                data_history.value = index_value
                # ensure the object stays separate in memory
                # while saving is pipelined
                data_history_objects[index] = data_history
                # add the saving of this object to the pipeline
                pipeline = data_history_objects[index].save(publish=False, pipeline=pipeline)
        try:
            database_response = pipeline.execute()

            # publish an update of this object type to pubsub
            logger.debug(f'publishing update to {data_history.__class__.__name__}')
            database.publish(
                data_history.__class__.__name__,
                f'{data_history.ticker}:{data_history.exchange}:{data_history.unix_timestamp}'
            )

            return Response({
                       'success': f'{sum(database_response)} db entries created'
                   }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(str(e))
            return Response({
                       'error': str(e)
                   }, status=status.HTTP_501_NOT_IMPLEMENTED)

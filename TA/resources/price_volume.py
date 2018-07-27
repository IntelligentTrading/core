from flask_restful import Resource, reqparse
from TA.app import database, logger
from TA.storages.data.pv_history import defualt_price_indexes, default_volume_indexes
from TA.storages.abstract.timeseries_storage import StorageException



from TA.storages.data.price import PriceStorage


# ["open_price", "close_price", "low_price", "high_price",
# "midpoint_price", "mean_price", "price_variance",
# "open_volume", "close_volume", "low_volume", "high_volume",]


class PriceVolumeAPI(Resource):

    def put(self, ticker):
        """
        This should receive a json dictionary of
        5 min resampled price and/or volume
        for the upcoming or nearly past 5min period
        closing at the provided unix timestamp
        where timestamp is an int divisible by 300s (5 min)
        """

        if not ticker.count('_') == 1:  # check format is like "ETH_BTC"
            logger.error(f'ticker {ticker} should be in format like ETH_BTC')
            return {
                       'error': f'ticker {ticker} does match required format ETH_BTC'
                   }, 400  #bad request

        # PARSE THE DATA
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', type=str, required=True, location='json')
        parser.add_argument('exchange', type=str, required=True, location='json')
        parser.add_argument('timestamp', type=int, required=True, location='json')

        for index in (defualt_price_indexes + default_volume_indexes):
            parser.add_argument(index, location='json', required=False)
        args = parser.parse_args()

        # SAVE VALUES IN REDIS USING PriceStorage OBJECT
        pipeline = database.pipeline(transaction=False)

        try:
            p = PriceStorage(ticker=ticker or args['ticker'],
                             exchange=args['exchange'],
                             timestamp=args['timestamp'])
        except StorageException as e:
            return {'error': str(e)}, 400  #bad request

        for index in defualt_price_indexes:
            if index in args:
                p.index = index
                p.value = args[index]
                pipeline = p.save(pipeline=pipeline)

        # v = VolumeStorage(ticker=args['ticker'],
        #                  exchange=args['exchange'],
        #                  timestamp=args['timestamp'])
        # for index in volume_indexes:
        #     if args[index]:
        #         v.index = index
        #         v.value = args[index]
        #         pipeline = v.save(pipeline=pipeline)

        try:
            database_response = pipeline.execute()
            return {
                       'success': f'{sum(database_response)} db entries created'
                   }, 201  #created

        except Exception as e:
            return {
                       'error': str(e)
                   }, 501  # not implented

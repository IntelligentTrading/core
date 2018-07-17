from abc import ABC
from flask_restful import Resource, Api, reqparse
import logging
from TA.app import db
from TA.storages.price import Price as PriceStorage


from TA.storages.price import price_indexes, volume_indexes
# ["open_price", "close_price", "low_price", "high_price",
# "midpoint_price", "mean_price", "price_variance",
# "open_volume", "close_volume", "low_volume", "high_volume",]
price_volume_indexes = price_indexes + volume_indexes


class PriceVolumeResampledAPI(Resource):

    def put(self):
        """
        This should receive a json dictionary of
        5 min resampled price and/or volume
        for the upcoming or nearly past 5min period
        closing at the provided unix timestamp
        where timestamp is an int divisible by 300s (5 min)
        """

        # PARSE THE DATA
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', type=str, required=True, location='json')
        parser.add_argument('exchange', type=str, required=True, location='json')
        parser.add_argument('timestamp', type=int, required=True, location='json')
        for index in price_volume_indexes:
            parser.add_argument(index, location='json')
        args = parser.parse_args()

        # SAVE VALUES IN REDIS USING PriceStorage OBJECT
        pipeline = db.pipeline(transaction=False)

        p = PriceStorage(ticker=args['ticker'],
                         exchange=args['exchange'],
                         timestamp=args['timestamp'])

        for index in price_indexes:
            if args[index]:
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
            db_confirmation = pipeline.execute()
            return {"records_created": sum(db_confirmation)}, 201

        except Exception as e:
            return {"error": "one or more records could not be saved... " + str(e)}


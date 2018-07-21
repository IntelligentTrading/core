from abc import ABC
from flask_restful import Resource, reqparse
from TA.app import logger, database
from TA.storages.pv_history import PriceVolumeHistoryStorage, price_indexes, volume_indexes


class HistoricalDataAPI(Resource):

    # def get(self, ticker):
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('ticker', type=str, required=True)
    #     parser.add_argument('exchange', type=str)
    #     parser.add_argument('timestamp', type=int)
    #
    #     data = parser.parse_args()
    #     return {
    #         'price': int(db.get('price') or None)
    #     }

    def put(self, ticker):
        """
        This should receive a resampled price
        for the upcoming or nearly past 5min period
        where timestamp is divisible by 300s (5 min)
        and represents a resampled data point for
        :return:
        """

        parser = reqparse.RequestParser()
        parser.add_argument('exchange', type=str, required=True, location='json')
        parser.add_argument('timestamp', type=int, required=True, location='json')
        parser.add_argument('tickers', required=True, location='json')
        args = parser.parse_args()

        # todo: parse some data here and save using Price object
        pipeline = database.pipeline()

        for ticker in args['tickers']:

            data_history = PriceVolumeHistoryStorage(
                ticker=ticker,
                exchange=args['exchange'],
                timestamp=args['timestamp']
            )

            for index in ticker.keys():
                if index in price_indexes + volume_indexes:
                    data_history.index = index
                    data_history.value = ticker[index]
                    pipeline = data_history.save()

        try:
            database_response = pipeline.execute()
            return {
                       'success': f'{sum(database_response)} db entries created'
                   }, 201  # created

        except Exception as e:
            return {
                       'error': str(e)
                   }, 501  # not implented

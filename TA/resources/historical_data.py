from abc import ABC
from flask_restful import Resource, reqparse
from TA.app import logger, database
from TA.storages.pv_history import PriceVolumeHistoryStorage, price_indexes, volume_indexes


class HistoricalDataAPI(Resource):

    def get(self, ticker):
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', type=str, required=(False if ticker else True))
        parser.add_argument('exchange', type=str, required=False)
        parser.add_argument('timestamp', type=int, required=False)
        args = parser.parse_args()

        # # start query for ticker
        # if args.get('exchange'):
        #     # add 'exchange' to query for key
        # if args.get('timestamp'):
        #     # add 'timestamp' to query for key
        # else:
        #     # get the last one, largest timestamp value

        # db.get()

        return {'price': 123, 'volume': 456}, 200


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
        parser.add_argument('ticker', required=(False if ticker else True), location='json')
        for index in price_indexes + volume_indexes:
            parser.add_argument(index, required=False, location='json')
        args = parser.parse_args()

        # todo: use a pipeline
        # pipeline = database.pipeline()

        # CREATE OBJECT FOR STORAGE
        data_history = PriceVolumeHistoryStorage(
            ticker=ticker or args['ticker'],
            exchange=args['exchange'],
            timestamp=args['timestamp']
        )

        save_results = []

        for index in price_indexes + volume_indexes:
            if args.get(index):
                data_history.index = index
                data_history.value = args[index]

                # todo: replace results list with pipeline
                save_results.append(data_history.save())

        try:
            # database_response = pipeline.execute()
            return {
                       'success': f'{sum(save_results)} db entries created'
                   }, 201  # created

        except Exception as e:
            logger.error(str(e))
            return {
                       'error': str(e)
                   }, 501  # not implented

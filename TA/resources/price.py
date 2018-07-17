from abc import ABC
from flask_restful import Resource, Api, reqparse
import logging


class PriceAPI(Resource):

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

    def put(self):
        """
        This should receive a resampled price
        for the upcoming or nearly past 5min period
        where timestamp is divisible by 300s (5 min)
        and represents a resampled data point for
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ticker', type=str, required=True)
        parser.add_argument('exchange', type=str, required=True)
        parser.add_argument('timestamp', type=int, required=True)
        args = parser.parse_args()

        # todo: parse some data here and save using Price object


        # args = parser.parse_args()
        #

        return {}

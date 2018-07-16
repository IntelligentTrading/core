from abc import ABC
from flask_restful import Resource, Api
import logging
from TA.app import db

price_denominations_set = set(
    "open", "close", "low", "high", "midpoint", "mean", "variance"
)

class PriceException(Exception):
    pass

class Price(ABC):
    """
    stores prices in a sorted set unique to each ticker and exchange
    redis keys
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """

    def __init__(self, *args, **kwargs):
        self.ticker = kwargs['ticker']
        self.exchange = kwargs['exchange']
        self.denomination = kwargs.get('denomination', "mean")
        self.force_save = kwargs.get('force_save', False)

        self.value = kwargs.get('value')
        self.unix_timestamp = int(kwargs.get('timestamp'))

        if self.unix_timestamp % 300 != 0 or self.unix_timestamp < 1483228800:
            raise PriceException("fix your timestamp. should be % 300 and > 1483228800 (2017-01-01)")

    def __str__(self):
        return str(self.key)

    @property
    def key(self):
        if not self.force_save:
            if not self.denomination in price_denominations_set:
                raise PriceException("unknown denomination")
        return "{ticker}:{exchange}:{denomination}"

    def save(self):

        if not all(self.ticker, self.exchange,
                   self.denomination, self.value,
                   self.unix_timestamp):
            logging.critical("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceException("save error, missing data")

        # example >>> redis.zadd('my-key', 'name1', 1.1)
        db.zadd(self.key, self.value, int(self.unix_timestamp))


class PriceAPI(Resource):

    def get(self):
        return {
            'price': int(db.get('price') or None)
        }

    def post(self):

        # todo: parse some data here and save using Price object

        # args = parser.parse_args()
        #
        # db.set('price', price)
        return {}
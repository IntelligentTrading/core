from abc import ABC
import logging


price_indexes = [
    "open_price", "close_price", "low_price", "high_price",
    "midpoint_price", "mean_price", "price_variance",
]

volume_indexes = [
    "open_volume", "close_volume", "low_volume", "high_volume",
]


class PriceException(Exception):
    pass

class Price(ABC):
    """
    stores prices in a sorted set unique to each ticker and exchange
    redis keys
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """

    def __init__(self, *args, **kwargs):
        self.ticker = kwargs['ticker']
        self.exchange = kwargs['exchange']
        self.index = kwargs.get('index', "close")
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
            if not self.index in price_indexes:
                raise PriceException("unknown index")
        return "{ticker}:{exchange}:{index}:{timestamp}".format(
            ticker=self.ticker, exchange=self.exchange,
            index=self.index, timestamp=self.unix_timestamp)

    def save(self, pipeline=False):
        # meets basic requirements for saving
        if not all(self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp):
            logging.critical("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceException("save error, missing data")

        # example >>> redis.zadd('my-key', 'name1', 1.1)
        if pipeline:
            pipeline.zadd(self.key, self.value, int(self.unix_timestamp))
            return pipeline
        else:
            from TA.app import db
            return db.zadd(self.key, self.value, int(self.unix_timestamp))

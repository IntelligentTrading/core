import logging
from abc import ABC


class IndicatorException(Exception):
    pass


class AbstractIndicator(ABC):
    """
    stores prices in a sorted set unique to each ticker and exchange
    redis keys
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """

    def __init__(self, *args, **kwargs):
        self.ticker = kwargs['ticker']  # str eg. BTC_USD
        self.exchange = kwargs['exchange']  # str or int

        self.unix_timestamp = int(kwargs.get('timestamp'))  # int eg. 1483228800
        if self.unix_timestamp % 300 != 0 or self.unix_timestamp < 1483228800:
            raise IndicatorException("fix your timestamp. should be % 300 and > 1483228800 (2017-01-01)")
        # self.resample_period = 300  # 5 min
        self.db_key_suffix = ""

        self.force_save = kwargs.get('force_save', False)


    def __str__(self):
        return str(self.get_db_key())


    def get_db_key(self):
        if not self.force_save:
            # validate some rules here?
            pass
        return "{ticker}:{exchange}:{class_name}:{timestamp}".format(
            ticker=self.ticker, exchange=self.exchange,
            class_name=str(self.__class__.__name__+self.db_key_suffix),
            timestamp=self.unix_timestamp)


    def save(self, pipeline=False):
        # example >>> redis.zadd('my-key', 'name1', 1.1)
        if pipeline:
            pipeline.zadd(self.get_db_key(), self.value, int(self.unix_timestamp))
            return pipeline
        else:
            from TA.app import db
            return db.zadd(self.get_db_key(), self.value, int(self.unix_timestamp))


    class Meta:
        abstract = True


"""
We can scan the newest or oldest event ids with ZRANGE 4,
maybe later pulling the events themselves for analysis.

We can get the 10 or even 100 events immediately
before or after a timestamp with ZRANGEBYSCORE
combined with the LIMIT argument.

We can count the number of events that occurred
in a specific time period with ZCOUNT.

https://www.infoq.com/articles/redis-time-series
"""

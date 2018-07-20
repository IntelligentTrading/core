from TA.app import logger, TAException
from abc import ABC

class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass


class TimeseriesStorage(ABC):
    """
    stores things in a sorted set unique to each ticker and exchange
    redis keys
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """

    def __init__(self, *args, **kwargs):
        self.force_save = kwargs.get('force_save', False)

        # validate required param timestamp
        try:
            self.unix_timestamp = int(kwargs['timestamp'])  # int eg. 1483228800
        except KeyError:
            raise TimeseriesException("timestamp required for TimeseriesStorage objects")
        except ValueError:
            raise TimeseriesException(
                "timestamp must be castable as integer, received {ts}".format(
                    ts=kwargs.get('timestamp')))
        except Exception as e:
            raise StorageException(str(e))

        if self.unix_timestamp < 1483228800:
            raise TimeseriesException("timestamp before January 1st, 2017")

        # key for redis storage
        self.db_key = kwargs.get('key', self.__class__.__name__)
        self.db_key_prefix = kwargs.get('key_prefix', "")
        self.db_key_suffix = kwargs.get('key_suffix', "")


    def __str__(self):
        return str(self.get_db_key())


    def get_db_key(self):
        if not self.force_save:
            # validate some rules here?
            pass

        # default for self.db_key is already self.__class__.__name__
        return str(
            f'{self.db_key_prefix.strip(":")}:' +
            f'{self.db_key.strip(":")}' +
            f':{self.db_key_suffix.strip(":")}'
        )

    def save(self, pipeline=False):
        # example >>> redis.zadd('my-key', 'name1', 1.1)
        zadd_args = (self.get_db_key(), # set key name
                          f'{self.value}:{str(self.unix_timestamp)}', # item unique value
                          int(self.unix_timestamp) # timestamp as score (int or float)
                     )
        if pipeline:
            pipeline.zadd(*zadd_args)
            return pipeline
        else:
            from TA.app import db
            return db.zadd(*zadd_args)


    class Meta:
        abstract = True


class TimeseriesIndicatorStorage(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        try:
            self.ticker = kwargs['ticker']  # str eg. BTC_USD
            self.exchange = str(kwargs.get('exchange', ""))  # str or int
        except KeyError:
            raise TAException("Indicator requires a ticker as initial parameter!")
        except Exception as e:
            raise TAException(str(e))
        else:
            if self.ticker.find("_") <= 0:
                raise TAException("ticker should be like BTC_USD")
            if not self.exchange:
                logger.debug("----- NO 'exchange' VALUE! ARE YOU SURE? -----")
            
        # ALL INDICATORS ARE ASSUMED 5-MIN PERIOD RESAMPLED
        if self.unix_timestamp % 300 != 0:
            raise TimeseriesException("indicator timestamp should be % 300")
        # self.resample_period = 300  # 5 min

    def get_db_key(self):
        self.db_key_prefix = f'{self.ticker}:{self.exchange}:'
        # by default will return "{ticker}:{exchange}:{class_name}"
        return super().get_db_key()


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
